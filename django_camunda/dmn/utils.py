from datetime import datetime
from typing import List, Tuple

from lxml.etree import _Element

from .datastructures import DMNVariable
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


def handle_default_namespace(namespaces: dict) -> dict:
    updated_namespaces = {**namespaces}
    updated_namespaces["default"] = updated_namespaces[None]
    del updated_namespaces[None]
    return updated_namespaces


def extract_decision_definition_inputs(
    xml: _Element, definition_id: str
) -> List[DMNInputParameter]:
    namespaces = handle_default_namespace(xml.nsmap)

    decision_table = xml.xpath(
        ".//default:decision[@id=$definition_id]",
        namespaces=namespaces,
        definition_id=definition_id,
    )[0]
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
        input_expression = text_element.text or ""
        if input_expression in dependency_tables:
            input_vars += extract_decision_definition_inputs(xml, input_expression)
            continue

        input_vars.append(
            DMNInputParameter(
                id=input_element.attrib["id"],
                label=input_element.attrib.get("label", ""),
                expression=input_expression,
                type_ref=expression_element.attrib["typeRef"],
                input_variable=input_element.attrib.get(
                    f"{{{CAMUNDA_NS['camunda']}}}inputVariable", ""
                ),
            )
        )
    return input_vars


def extract_decision_definition_outputs(
    xml: _Element, definition_id: str
) -> List[DMNOutputParameter]:
    namespaces = handle_default_namespace(xml.nsmap)

    decision_table = xml.xpath(
        ".//default:decision[@id=$definition_id]",
        namespaces=namespaces,
        definition_id=definition_id,
    )[0]
    output_elements = decision_table.findall(".//output", namespaces=xml.nsmap)

    return [
        DMNOutputParameter(
            id=element.attrib["id"],
            label=element.attrib["label"],
            name=element.attrib["name"],
            type_ref=element.attrib["typeRef"],
        )
        for element in output_elements
    ]
