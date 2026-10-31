"""weather-cli: fetch a weather forecast from the command line."""
import argparse

DEFAULT_TIMEOUT = 60
DEFAULT_UNITS = "metric"


def fetch_forecast(city, days=7, units=DEFAULT_UNITS):
    """Return the forecast for `city` for the next `days` days."""
    return {"city": city, "days": days, "units": units}


def main():
    parser = argparse.ArgumentParser(prog="weather")
    parser.add_argument("city")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--units", default=DEFAULT_UNITS)
    args = parser.parse_args()
    print(fetch_forecast(args.city, units=args.units))


if __name__ == "__main__":
    main()
