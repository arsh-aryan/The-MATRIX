# weather-cli

A tiny command-line tool that prints a weather forecast.

## Usage
Run `weather London --max-retries 5` to retry failed requests more often.
The --timeout flag defaults to 30 seconds.
Use --units imperial to show temperatures in Fahrenheit.

## Python API
Call fetch_forecast(city) to get a 3 day forecast.
Use export_csv(forecast, path) to save results to a spreadsheet.

## Configuration
Units default to metric.
