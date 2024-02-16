from lxml import etree

from .client import get_client

CAMUNDA_NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "camunda": "http://camunda.org/schema/1.0/bpmn",
}


def get_bpmn(process_definition_id: str) -> etree._Element:
    """
    Retrieve the BPMN definition from a process definition ID.

    :returns: lxml etree Element instance.
    """
    client = get_client()
    bpmn_xml: str = client.get(f"process-definition/{process_definition_id}/xml")[
        "bpmn20_xml"
    ]

    # Camunda JSON API encodes as utf-8
    tree = etree.fromstring(bpmn_xml.encode("utf-8"))
    return tree
