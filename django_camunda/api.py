"""
Public Python API to interact with Activiti.
"""
from typing import List

from .camunda_models import ProcessDefinition, factory
from .client import get_client_class


def get_process_definitions() -> List[ProcessDefinition]:
    client = get_client_class()()
    response = client.get("process-definition", {"sortBy": "name", "sortOrder": "asc"})
    return factory(ProcessDefinition, response)
