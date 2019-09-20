from typing import Dict, Union

from celery import shared_task

from .client import get_client_class
from .interface import Variable


@shared_task
def start_process(
    process_key: str, business_key: str, variables: Dict[str, Union[Variable, dict]]
) -> Dict[str, str]:
    """
    Start a process in the camunda process engine.

    The result is stored in the Celery result backend, so you can match a task
    ID with the resulting process instance.

    :param process_key: the key that a process is deployed with. Will start the
      latest vesion of this process.
    :param business_key: the camunda business key that applies.
    :param variables: a dictionary where the keys are variable names relevant
      for the process. Values can be instances of :class:`Variable` for complex/
      custom types, or simple dicts in the camunda format. See
      https://docs.camunda.org/manual/7.11/reference/rest/process-definition/post-start-process-instance/#starting-a-process-instance-at-its-default-initial-activity
      for an example.
    :return: a dict with the details of the started process instance
    """
    client = get_client_class()()

    variables = {
        key: var.serialize() if isinstance(var, Variable) else var
        for key, var in variables.items()
    }

    body = {
        "businessKey": business_key,
        "withVariablesInReturn": False,
        "variables": variables,
    }

    response = client.request(
        f"process-definition/key/{process_key}/start", method="POST", json=body
    )

    self_rel = next((link for link in response["links"] if link["rel"] == "self"))
    instance_url = self_rel["href"]

    return {"instance_id": response["id"], "instance_url": instance_url}
