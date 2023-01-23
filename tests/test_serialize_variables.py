from collections import OrderedDict
from datetime import date, datetime

from django_camunda.utils import serialize_variables


def test_serialize_variables():
    variables = {
        "bool": True,
        "date": date(1999, 12, 31),
        "datetime": datetime(1999, 12, 31, 23, 59, 59),
        "integer": 1,
        "float": 1.0,
        "str": "some-string",
        "none": None,
        "dict": {1: 1},
        "list": [1],
        "ordered_dict": OrderedDict([(1, 1)]),
    }

    serialize_variables(variables) == {
        "bool": {"type": "Boolean", "value": True},
        "date": {"type": "String", "value": "1999-12-31"},
        "datetime": {"type": "Date", "value": "1999-12-31T23:59:59"},
        "integer": {"type": "Integer", "value": 1},
        "float": {"type": "Double", "value": 1.0},
        "str": {"type": "String", "value": "some-string"},
        "none": {"type": "Null", "value": None},
        "dict": {"type": "Json", "value": '{"1": 1}'},
        "list": {"type": "Json", "value": "[1]"},
        "ordered_dict": {"type": "Json", "value": '{"1": 1}'},
    }
