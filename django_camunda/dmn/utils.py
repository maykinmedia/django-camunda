from datetime import datetime
from typing import Tuple

from defusedxml import ElementTree as ET

from .datastructures import DMNVariable, IntrospectionResult

CAMUNDA_NS = {
    "dmn": "https://www.omg.org/spec/DMN/20191111/MODEL/",
    "camunda": "http://camunda.org/schema/1.0/dmn",
}


TYPEREF_MAP = {
    "string": str,
    "boolean": bool,
    "integer": int,
    "long": int,
    "double": float,
    "date": datetime,
    None: str,
}


def process_input_var(input_var) -> Tuple[str, DMNVariable]:
    input_expression_element = input_var.find("./dmn:inputExpression", CAMUNDA_NS)

    # see if we can find a variable/expression hint
    camunda_input_variable_attrib = f"{{{CAMUNDA_NS['camunda']}}}inputVariable"
    input_expression = input_var.attrib.get(camunda_input_variable_attrib)
    if input_expression:
        expression_hint = input_expression
    elif input_expression_element:
        expression_hint = (
            input_expression_element.find("./dmn:text", CAMUNDA_NS).text or ""
        )
    else:
        expression_hint = ""

    # type ref
    type_ref = (
        input_expression_element.attrib["typeRef"] if input_expression_element else None
    )

    return DMNVariable(
        label=input_var.attrib.get("label", ""),
        type=TYPEREF_MAP.get(type_ref, str),
        expression_hint=expression_hint,
    )


def process_output_var(output_var) -> Tuple[str, DMNVariable]:
    name = output_var.attrib["name"]
    label = output_var.attrib["label"] or name
    type_ref = output_var.attrib["typeRef"]
    return name, DMNVariable(label=label, type=TYPEREF_MAP.get(type_ref, str))


def parse_dmn(xml: str) -> IntrospectionResult:
    tree = ET.fromstring(xml)
    input_vars = tree.findall(".//dmn:input", CAMUNDA_NS)
    output_vars = tree.findall(".//dmn:output", CAMUNDA_NS)
    inputs = [process_input_var(input_var) for input_var in input_vars]
    outputs = dict((process_output_var(output_var) for output_var in output_vars))
    return IntrospectionResult(inputs=inputs, output=outputs)
