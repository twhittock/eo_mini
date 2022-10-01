"""Tests for EO Mini integration."""

import json


def json_load_file(data_file):
    "Get json data from a file in the example data folder"
    with open(f"tests/example_data/{data_file}", "r", encoding="utf-8") as fh:
        return json.load(fh)
