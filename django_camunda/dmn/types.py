from typing import Literal, TypedDict


class DMNInputParameter(TypedDict):
    # Unique identifier of the decision table input
    id: str
    label: str
    # Specifies how the value of the input clause is generated.
    # It usually simple references a variable which is available during the evaluation.
    expression: str
    # The type of the input expression after being evaluated.
    type_ref: Literal["string", "integer", "long", "boolean", "date", "double"]


class DMNOutputParameter(TypedDict):
    id: str
    label: str
    # Used to reference the value of the output.
    name: str
    type_ref: Literal["string", "integer", "long", "boolean", "date", "double"]
