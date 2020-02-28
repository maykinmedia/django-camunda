import logging
from typing import Dict, Optional, Union

from celery import shared_task

from .client import get_client
from .interface import Variable

logger = logging.getLogger(__name__)


@shared_task
def start_process(
    process_key: Optional[str] = None,
    process_id: Optional[str] = None,
    business_key: Optional[str] = None,
    variables: Dict[str, Union[Variable, dict]] = None,
) -> Dict[str, str]:
    """
    Start a process in the camunda process engine.

    The result is stored in the Celery result backend, so you can match a task
    ID with the resulting process instance.

    :param process_key: the key that a process is deployed with. Will start the
      latest vesion of this process.
    :param process_id: the id of a process. Will start this particular process version.
    :param business_key: the camunda business key that applies.
    :param variables: a dictionary where the keys are variable names relevant
      for the process. Values can be instances of :class:`Variable` for complex/
      custom types, or simple dicts in the camunda format. See
      https://docs.camunda.org/manual/7.11/reference/rest/process-definition/post-start-process-instance/#starting-a-process-instance-at-its-default-initial-activity
      for an example.
    :return: a dict with the details of the started process instance
    """
    logger.debug(
        "Received process start: process_key=%s, process_id=%s", process_key, process_id
    )
    if not (process_key or process_id):
        raise ValueError("Provide a process key or process ID")

    client = get_client()
    variables = variables or {}

    _variables = {
        key: var.serialize() if isinstance(var, Variable) else var
        for key, var in variables.items()
    }

    if process_id:
        endpoint = f"process-definition/{process_id}/start"
    else:
        endpoint = f"process-definition/key/{process_key}/start"

    body = {
        "businessKey": business_key,
        "withVariablesInReturn": False,
        "variables": _variables,
    }

    response = client.post(endpoint, json=body)

    self_rel = next((link for link in response["links"] if link["rel"] == "self"))
    instance_url = self_rel["href"]

    logger.info("Started process instance %s", response["id"])

    return {"instance_id": response["id"], "instance_url": instance_url}
