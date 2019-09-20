"""
Middleware to transform data from/to camunda.
"""
import json
from dataclasses import dataclass
from typing import Union


@dataclass
class Variable:
    data: Union[list, dict]

    serialization_data_format = "application/json"
    object_type_name = None

    def serialize(self) -> dict:
        value_info = {
            "serializationDataFormat": self.serialization_data_format,
            "objectTypeName": self.object_type_name,
        }
        self.pre_process()
        return {"type": "json", "value": json.dumps(self.data), "valueInfo": value_info}

    def pre_process(self):
        pass
