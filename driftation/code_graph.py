"""Step 1: build a small knowledge graph of the Python code with ast + networkx.

Nodes are code items, named "<kind>:<name>":
  function:fetch   class:Client   constant:TIMEOUT   flag:--max-retries   param:fetch.timeout
Edges say how they relate: "defines" (function -> its params), "calls" (function -> function),
"uses" (function or flag -> constant).
"""
import ast
import warnings

import networkx as nx

from .config_files import extract_config, is_config

FLAG_FUNCS = {"add_argument", "option", "argument"}  # argparse and click


def node_id(kind, name):
    return f"{kind}:{name}"


def display_name(kind, name):
    """The text we look for in docs: a param "fetch.timeout" is written as "timeout"."""
    return name.split(".")[-1] if kind == "param" else name


def extract(source):
    """Find the code items in one Python file.

    Returns (symbols, links):
      symbols: {(kind, name): {"value": text or None, "line": int}}
      links:   [(from_kind, from_name, edge, to_name)]  # to_name is resolved later
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # old code can trigger harmless SyntaxWarnings
            tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return {}, []
    symbols, links = {}, []

    # Module and class level constants, e.g. TIMEOUT = 30
    for owner in [tree] + [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        for stmt in owner.body:
            for name, value in _assigned(stmt):
                if name.isupper() or isinstance(value, ast.Constant):
                    symbols[("constant", name)] = {"value": _text(value), "line": stmt.lineno}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols[("class", node.name)] = {"value": None, "line": node.lineno}
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols[("function", node.name)] = {
                "value": None,
                "line": node.lineno,
                "body": _body_fingerprint(node),  # used to spot behaviour changes
                "code": (ast.get_source_segment(source, node) or "")[:1500],
            }
            for arg, default in _params(node):
                symbols[("param", f"{node.name}.{arg}")] = {"value": _text(default), "line": node.lineno}
                links.append(("function", node.name, "defines", f"param:{node.name}.{arg}"))
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name):
                    links.append(("function", node.name, "calls", f"function:{inner.func.id}"))
                elif isinstance(inner, ast.Name) and isinstance(inner.ctx, ast.Load):
                    links.append(("function", node.name, "uses", f"constant:{inner.id}"))
        elif isinstance(node, ast.Call):
            flag = _flag(node)
            if flag:
                name, default = flag
                symbols[("flag", name)] = {"value": _text(default), "line": node.lineno}
                # A flag whose default is a constant, e.g. default=DEFAULT_RETRIES
                for inner in ast.walk(default) if default is not None else []:
                    if isinstance(inner, ast.Name):
                        links.append(("flag", name, "uses", f"constant:{inner.id}"))
    return symbols, links


def build_graph(tree):
    """Build the graph for every .py file and config file in a GitTree or Folder."""
    graph = nx.DiGraph()
    all_links = []
    for path in tree.list_files():
        if path.endswith(".py"):
            symbols, links = extract(tree.read(path) or "")
        elif is_config(path):
            symbols, links = extract_config(path, tree.read(path) or ""), []
        else:
            continue
        for (kind, name), info in symbols.items():
            graph.add_node(node_id(kind, name), kind=kind, name=name, file=path, **info)
        all_links += links
    # Only keep edges whose target really exists in the project
    for kind, name, edge, target in all_links:
        source = node_id(kind, name)
        if target in graph and source != target:
            graph.add_edge(source, target, label=edge)
    return graph


def walk(graph, start, max_steps=2):
    """Return {node: path_from_start} for nodes within `max_steps` edges (any direction)."""
    if start not in graph:
        return {start: [start]}
    paths = {start: [start]}
    frontier = [start]
    for _ in range(max_steps):
        next_frontier = []
        for node in frontier:
            for neighbour in list(graph.successors(node)) + list(graph.predecessors(node)):
                if neighbour not in paths:
                    paths[neighbour] = paths[node] + [neighbour]
                    next_frontier.append(neighbour)
        frontier = next_frontier
    return paths


def _body_fingerprint(func):
    """A text that changes only when the function's code changes (its docstring is ignored)."""
    body = func.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
        body = body[1:]
    return "\n".join(ast.dump(stmt) for stmt in body)


def _assigned(stmt):
    """(name, value) pairs for `X = value` and `X: int = value`."""
    if isinstance(stmt, ast.Assign):
        return [(t.id, stmt.value) for t in stmt.targets if isinstance(t, ast.Name)]
    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value:
        return [(stmt.target.id, stmt.value)]
    return []


def _params(func):
    """(arg_name, default_node_or_None) for each parameter, skipping self/cls."""
    args = func.args.posonlyargs + func.args.args
    defaults = [None] * (len(args) - len(func.args.defaults)) + list(func.args.defaults)
    pairs = list(zip([a.arg for a in args], defaults))
    pairs += list(zip([a.arg for a in func.args.kwonlyargs], func.args.kw_defaults))
    return [(name, default) for name, default in pairs if name not in ("self", "cls")]


def _flag(call):
    """For add_argument("--max-retries", default=3) return ("--max-retries", <default node>)."""
    func = call.func
    func_name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
    if func_name not in FLAG_FUNCS:
        return None
    flags = [
        a.value for a in call.args
        if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.startswith("-")
    ]
    if not flags:
        return None
    long_flags = [f for f in flags if f.startswith("--")]
    default = next((k.value for k in call.keywords if k.arg == "default"), None)
    return (long_flags or flags)[0], default


def _text(node):
    return ast.unparse(node) if node is not None else None
