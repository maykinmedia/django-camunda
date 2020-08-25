"""
Public Python API to interact with Activiti.
"""
from typing import Any, Dict, Iterable, List, Optional

import requests

from .camunda_models import ProcessDefinition, factory
from .client import get_client
from .types import CamundaId, ProcessVariables
from .utils import deserialize_variable, serialize_variable


def get_process_definitions() -> List[ProcessDefinition]:
    client = get_client()
    response = client.get("process-definition", {"sortBy": "name", "sortOrder": "asc"})
    return factory(ProcessDefinition, response)


def get_start_form_variables(
    process_key: Optional[str] = None, process_id: Optional[str] = None
) -> ProcessVariables:
    """
    Get the start form variables from the Camunda process.

    If defaults are configured in the Camunda process, these will be returned as value.

    A process ID is more specific than a process key, so if both are provided, the
    process ID will be used.
    """
    if not (process_key or process_id):
        raise ValueError("Provide a process key or process ID")

    if process_id:
        endpoint = f"process-definition/{process_id}/form-variables"
    else:
        endpoint = f"process-definition/key/{process_key}/form-variables"

    # TODO: do any necessary type casting
    client = get_client()
    variables = client.get(endpoint, underscoreize=False)

    return variables


def _get_variable(kind: str, id_ref: CamundaId, name: str) -> Any:
    client = get_client()
    path = f"{kind}/{id_ref}/variables/{name}"
    response_data = client.get(
        path, params={"deserializeValues": "false"}, underscoreize=False
    )
    return deserialize_variable(response_data)


def _get_variables(kind: str, id_ref: CamundaId) -> Dict[str, Any]:
    client = get_client()
    path = f"{kind}/{id_ref}/variables"
    response_data = client.get(
        path, params={"deserializeValues": "false"}, underscoreize=False
    )
    variables = {
        name: deserialize_variable(variable) for name, variable in response_data.items()
    }
    return variables


def get_process_instance_variable(instance_id: CamundaId, name: str) -> Any:
    return _get_variable("process-instance", instance_id, name)


def get_all_process_instance_variables(instance_id: CamundaId) -> Dict[str, Any]:
    return _get_variables("process-instance", instance_id)


def get_task_variable(task_id: CamundaId, name: str, default=None) -> Any:
    try:
        return _get_variable("task", task_id, name)
    except requests.HTTPError as exc:
        if exc.response.status_code == 404:  # variable not set
            return default
        raise


def get_task_variables(task_id: CamundaId) -> Dict[str, Any]:
    return _get_variables("task", task_id)


def send_message(
    name: str,
    process_instance_ids: Iterable[CamundaId],
    variables: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Send a BPMN message into running process instances, with optional process variables.

    :param name: Name/ID of the message definition, extract this from the process.
    :param process_instance_ids: an iterable of process instance IDs, can be uuid
      instances or strings.
    :param variables: Optional mapping of ``{name: value}`` process variables. Will be
      serialized as part of the message sending.
    """
    client = get_client()
    variables = (
        {name: serialize_variable(value) for name, value in variables.items()}
        if variables
        else None
    )
    for instance_id in process_instance_ids:
        body = {
            "messageName": name,
            "processInstanceId": instance_id,
            "processVariables": variables or {},
        }
        client.post("message", json=body)


def complete_task(task_id: CamundaId, variables: dict) -> None:
    client = get_client()
    variables = {name: serialize_variable(value) for name, value in variables.items()}
    client.post(f"task/{task_id}/complete", json={"variables": variables})
