"""
Public Python API to interact with Activiti.
"""
import uuid
from typing import Dict, List, Optional, Union

from .camunda_models import ProcessDefinition, factory
from .client import get_client
from .types import JSONObject, ProcessVariable, ProcessVariables
from .utils import deserialize_variable


def get_process_definitions() -> List[ProcessDefinition]:
    client = get_client()
    response = client.get("process-definition", {"sortBy": "name", "sortOrder": "asc"})
    return factory(ProcessDefinition, response)


def get_start_form_variables(
    process_key: Optional[str] = None, process_id: Optional[str] = None
) -> Dict[str, JSONObject]:
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


def get_process_instance_variable(
    instance_id: Union[uuid.UUID, str], name: str
) -> ProcessVariable:
    client = get_client()

    response_data = client.get(
        f"process-instance/{instance_id}/variables/{name}",
        params={"deserializeValues": "false"},
        underscoreize=False,
    )
    return deserialize_variable(response_data)


def get_all_process_instance_variables(
    instance_id: Union[uuid.UUID, str]
) -> ProcessVariables:
    client = get_client()

    response_data = client.get(
        f"process-instance/{instance_id}/variables",
        params={"deserializeValues": "false"},
        underscoreize=False,
    )
    variables = {
        name: deserialize_variable(variable) for name, variable in response_data.items()
    }
    return variables
