from datetime import datetime
from typing import List, Tuple

from lxml import etree
from lxml.etree import _Element

from .datastructures import DMNVariable, IntrospectionResult
from .types import DMNInputParameter, DMNOutputParameter

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
    elif input_expression_element is not None:
        expression_hint = (
            input_expression_element.find("./dmn:text", CAMUNDA_NS).text or ""
        )
    else:
        expression_hint = ""

    # type ref
    type_ref = (
        input_expression_element.attrib["typeRef"]
        if input_expression_element is not None
        else None
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


def parse_dmn(xml: bytes) -> IntrospectionResult:
    tree = etree.fromstring(xml)
    input_vars = tree.findall(".//dmn:input", CAMUNDA_NS)
    output_vars = tree.findall(".//dmn:output", CAMUNDA_NS)
    inputs = [process_input_var(input_var) for input_var in input_vars]
    outputs = dict((process_output_var(output_var) for output_var in output_vars))
    return IntrospectionResult(inputs=inputs, output=outputs)


def extract_decision_definition_inputs(
    xml: _Element, definition_id: str
) -> List[DMNInputParameter]:
    decision_table = xml.find(
        f".//decision[@id='{definition_id}']", namespaces=xml.nsmap
    )
    input_elements = decision_table.findall(".//input", namespaces=xml.nsmap)
    dependency_tables = [
        dependency.attrib["href"].lstrip("#")
        for dependency in decision_table.findall(
            ".//requiredDecision", namespaces=xml.nsmap
        )
    ]

    input_vars = []
    for input_element in input_elements:
        expression_element = input_element.find("inputExpression", namespaces=xml.nsmap)
        text_element = expression_element.find("text", namespaces=xml.nsmap)
        input_expression = text_element.text
        if input_expression in dependency_tables:
            input_vars += extract_decision_definition_inputs(xml, input_expression)
            continue

        input_vars.append(
            DMNInputParameter(
                id=input_element.attrib["id"],
                label=input_element.attrib["label"],
                expression=input_expression,
                type_ref=expression_element.attrib["typeRef"],
            )
        )
    return input_vars


def extract_decision_definition_outputs(
    xml: _Element, definition_id: str
) -> List[DMNOutputParameter]:
    decision_table = xml.find(
        f".//decision[@id='{definition_id}']", namespaces=xml.nsmap
    )
    output_elements = decision_table.findall(".//output", namespaces=xml.nsmap)

    output_vars = [
        DMNOutputParameter(
            id=element.attrib["id"],
            label=element.attrib["label"],
            name=element.attrib["name"],
            type_ref=element.attrib["typeRef"],
        )
        for element in output_elements
    ]
    return output_vars
