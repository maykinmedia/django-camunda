import json
from datetime import date, datetime
from typing import Any, Dict, List, Tuple, Union

import inflection
from dateutil import parser

from .constants import LATEST
from .types import ProcessVariable


def parse_definition(definition_ref: str) -> Tuple[bool, str]:
    """
    Given a definition reference, parse it to determine if it's a specific version.
    """
    bits = definition_ref.split(":")
    if len(bits) == 2 and bits[1] == LATEST:
        return (True, bits[0])
    return (False, definition_ref)


def noop(val):
    return val


def underscoreize(data: Union[List, Dict, str, None]) -> Union[List, Dict, str, None]:
    if isinstance(data, list):
        return [underscoreize(item) for item in data]

    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = inflection.underscore(key)
            # variables are dynamic names, can't make assumptions!
            if key == "variables":
                new_data[new_key] = value
            else:
                new_data[new_key] = underscoreize(value)
        return new_data

    return data


TYPE_MAP = {
    bool: ("Boolean", noop),
    date: (
        "String",
        lambda d: d.isoformat(),
    ),  # Date object requires time information, which we don't have
    datetime: ("Date", lambda d: d.isoformat()),
    int: ("Integer", noop),
    float: ("Double", noop),
    str: ("String", noop),
    type(None): ("Null", noop),
    dict: ("Json", json.dumps),
    list: ("Json", json.dumps),
}


REVERSE_TYPE_MAP = {
    "date": parser.parse,
    "json": json.loads,
    "integer": int,
    "short": int,
    "long": int,
}


def serialize_variable(value: Any) -> ProcessVariable:
    val_type = type(value)
    if val_type not in TYPE_MAP:
        raise NotImplementedError(f"Type {val_type} is not implemented yet")

    type_name, converter = TYPE_MAP[val_type]
    return {"type": type_name, "value": converter(value)}


def deserialize_variable(variable: ProcessVariable) -> Any:
    var_type = variable.get("type", "String")
    converter = REVERSE_TYPE_MAP.get(var_type.lower())
    if converter:
        value = converter(variable["value"])
    else:
        value = variable["value"]  # a JSON primitive that maps to proper python objects

    return value
