import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from dateutil.parser import parse

from .types import JSONObject

CONVERTERS = {
    type(None): lambda x: None,
    uuid.UUID: lambda value: uuid.UUID(value),
    datetime: parse,
}


class Model:
    def __post_init__(self):
        self._type_cast()

    def _type_cast(self):
        for attr, typehint in self.__annotations__.items():
            value = getattr(self, attr)

            if typehint is None:
                typehint = type(None)

            # support for Optional
            if hasattr(typehint, "__origin__") and typehint.__origin__ is Union:
                typehint = typehint.__args__

                if value is None:
                    continue

                # Optional is ONE type combined with None
                typehint = next(t for t in typehint.__args__ if t is not None)

            if isinstance(value, typehint):
                continue

            converter = CONVERTERS[typehint]
            setattr(self, attr, converter(value))


def factory(model: type, data: Union[JSONObject, List[JSONObject]]) -> type:
    _is_collection = isinstance(data, list)

    known_kwargs = list(model.__annotations__.keys())

    def _normalize(kwargs: dict):
        to_keep = {key: value for key, value in kwargs.items() if key in known_kwargs}
        return to_keep

    if not _is_collection:
        data = [data]

    instances = [model(**_normalize(_raw)) for _raw in data]

    if not _is_collection:
        instances = instances[0]
    return instances


@dataclass
class Task(Model):
    id: uuid.UUID
    name: str
    assignee: None
    created: datetime
    due: Optional[datetime]
    follow_up: None
    delegation_state: None
    description: None
    execution_id: str
    owner: None
    parent_task_id: None
    priority: int
    process_definition_id: str
    process_instance_id: uuid.UUID
    task_definition_key: str
    case_execution_id: None
    case_instance_id: None
    case_definition_id: None
    suspended: bool
    form_key: None
    tenant_id: None

    def claim(self) -> None:
        from bing.service.camunda import claim_task

        claim_task(self.id)

    def complete(self, variables: Dict[str, Any]) -> None:
        from bing.service.camunda import complete_task

        complete_task(self.id, variables)


@dataclass
class ProcessDefinition(Model):
    id: str
    key: str
    name: str
    category: str
    version: int
    deployment_id: uuid.UUID
    resource: str  # filename
    startable_in_tasklist: bool
    suspended: bool
    description: Optional[str] = None
    tenant_id: Optional[str] = None
    version_tag: Optional[str] = None  # unsure
    diagram: Optional[str] = None  # unsure
    history_time_to_live: Optional[str] = None  # unsure
