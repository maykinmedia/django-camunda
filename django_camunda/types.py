import uuid
from typing import Any, Dict, List, TypedDict, Union

JSONPrimitive = Union[str, int, None, float]
JSONValue = Union[JSONPrimitive, "JSONObject", List["JSONValue"]]
JSONObject = Dict[str, JSONValue]

# {"type": "Integer", "value": 42}
class ProcessVariable(TypedDict):
    """
    Camunda-serialized variable.
    """

    type: str
    value: JSONPrimitive


ProcessVariables = Dict[str, ProcessVariable]
"""
Camunda-serialized variables mapping.
"""

VariablesMapping = Dict[str, Any]
"""
Camunda-deserialized variables mapping.
"""

CamundaId = Union[str, uuid.UUID]
"""
Internal Camunda object ID.
"""
