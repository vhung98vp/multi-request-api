# Multi-Request API

This is a Flask-based API that sends multiple requests to a list of URLs and returns the first successful response. It is designed to handle concurrent requests efficiently using Python's `ThreadPoolExecutor`.

## Features

- Sends multiple requests to a list of URLs.
- Returns the first successful response (HTTP 200).
- Supports query parameters.
- Configurable number of requests and URLs via environment variables.

## Requirements

- Python 3.10 or higher
- Flask 3.1.0
- Requests 2.32.3

# Endpoints:
- [GET] /get: Any query parameters passed to this endpoint will be forwarded to the target URLs.