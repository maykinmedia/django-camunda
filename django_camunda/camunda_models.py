import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union

from dateutil.parser import parse

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
