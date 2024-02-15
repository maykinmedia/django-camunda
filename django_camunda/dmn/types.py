from typing import Literal, TypedDict

CamundaDataType = Literal["string", "integer", "long", "boolean", "date", "double"]


class DMNInputParameter(TypedDict):
    # Unique identifier of the decision table input
    id: str
    label: str
    # Specifies how the value of the input clause is generated.
    # It usually simple references a variable which is available during the evaluation.
    expression: str
    # The type of the input expression after being evaluated.
    type_ref: CamundaDataType
    # https://docs.camunda.org/manual/7.20/reference/dmn/decision-table/input/#input-variable-name
    # When the input expression is evaluated then the return value is stored in a variable with the name found in the
    # camunda:inputVariable attribute.
    input_variable: str


class DMNOutputParameter(TypedDict):
    id: str
    label: str
    # Used to reference the value of the output.
    name: str
    type_ref: CamundaDataType
