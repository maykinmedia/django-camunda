import json
import logging
from typing import Any, Dict, Optional

from defusedxml import ElementTree as ET

from ..client import Camunda, get_client
from ..types import VariablesMapping
from ..utils import deserialize_variables, serialize_variables
from .datastructures import IntrospectionResult
from .utils import parse_dmn

logger = logging.getLogger(__name__)


def evaluate_dmn(
    dmn_key: str,
    *,
    dmn_id: str = "",
    input_values: VariablesMapping,
    client: Optional[Camunda] = None,
) -> VariablesMapping:
    """
    Evaluate the specified DMN table with the given input values.

    If an ID is provided, the DMN table with the given ID is used. Otherwise, the most
    recent DMN table matching the given key will be evaluated.

    The return value is the output deserialized to Python types.
    """
    logger.debug(
        "Evaluating DMN table with key %s and dmn_id %s",
        dmn_key,
        dmn_id,
    )
    client = client or get_client()
    serialized = serialize_variables(input_values)

    logger.debug("Input data: %r", serialized)

    with client:
        id_part = dmn_id if dmn_id else f"key/{dmn_key}"
        result: list = client.post(
            f"decision-definition/{id_part}/evaluate",
            json={"variables": serialized},
            underscoreize=False,
        )

    # TODO: check output with multiple values/strategies - Camunda returns a list
    # of outputs
    output_variables = {}
    for output in result:
        output_variables.update(deserialize_variables(output))
    return output_variables


def introspect_dmn(
    dmn_key: str, *, dmn_id: str = "", client: Optional[Camunda] = None
) -> IntrospectionResult:
    client = client or get_client()
    id_part = dmn_id if dmn_id else f"key/{dmn_key}"
    with client:
        xml = client.get(f"decision-definition/{id_part}/xml")["dmn_xml"]
    return parse_dmn(xml)
