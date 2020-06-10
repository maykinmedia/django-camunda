import uuid
from typing import Dict, List, Union

JSONPrimitive = Union[str, int, None, float]
JSONValue = Union[JSONPrimitive, "JSONObject", List["JSONValue"]]
JSONObject = Dict[str, JSONValue]

ProcessVariable = Dict[str, JSONPrimitive]  # {"type": "Integer", "value": 42}
ProcessVariables = Dict[str, ProcessVariable]

CamundaId = Union[str, uuid.UUID]
