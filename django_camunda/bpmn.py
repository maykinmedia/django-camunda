from defusedxml import ElementTree as ET

from .client import get_client

CAMUNDA_NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "camunda": "http://camunda.org/schema/1.0/bpmn",
}


def get_bpmn(process_definition_id: str) -> ET:
    """
    Retrieve the BPMN definition from a process definition ID.

    :returns: defusedxml ElementTree instance.
    """
    client = get_client()
    bpmn_xml = client.get(f"process-definition/{process_definition_id}/xml")[
        "bpmn20_xml"
    ]

    tree = ET.fromstring(bpmn_xml)
    return tree
