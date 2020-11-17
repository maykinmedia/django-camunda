import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from dateutil.parser import parse

from .types import JSONObject


def noop(value: Any) -> Any:
    return value


CONVERTERS = {
    type(None): lambda x: None,
    str: noop,
    int: noop,
    float: noop,
    dict: noop,  # TODO: recurse?
    uuid.UUID: lambda value: uuid.UUID(value),
    datetime: parse,
    date: date.fromisoformat,
}


class Model:
    def __post_init__(self):
        self._type_cast()

    def _type_cast(self):
        annotations = get_all_annotations(self.__class__)
        for attr, typehint in annotations.items():
            value = getattr(self, attr)

            if typehint is None:
                typehint = type(None)

            # support for Optional
            if hasattr(typehint, "__origin__") and typehint.__origin__ is Union:
                typehint = typehint.__args__

                if value is None:
                    continue

                # Optional is ONE type combined with None
                typehint = next(t for t in typehint if t is not None)

            if isinstance(value, typehint):
                continue

            converter = CONVERTERS[typehint]
            setattr(self, attr, converter(value))


def get_all_annotations(cls: type) -> Dict[str, Any]:
    annotations = {}
    for supercls in cls.__bases__:
        super_annotations = get_all_annotations(supercls)
        annotations.update(super_annotations)

    # Follow MRO - most specific top-level class wins, otherwise left-to-right
    if hasattr(cls, "__annotations__"):
        annotations.update(cls.__annotations__)
    return annotations


def factory(
    model: type, data: Union[JSONObject, List[JSONObject]]
) -> Union[type, List[type]]:
    _is_collection = isinstance(data, list)

    known_kwargs = list(get_all_annotations(model).keys())

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
    assignee: Optional[str]
    created: datetime
    due: Optional[datetime]
    follow_up: Optional[str]
    delegation_state: Optional[str]
    description: Optional[str]
    execution_id: str
    owner: Optional[str]
    parent_task_id: Optional[uuid.UUID]
    priority: int
    process_definition_id: str
    process_instance_id: uuid.UUID
    task_definition_key: str
    case_execution_id: Optional[str]
    case_instance_id: Optional[str]
    case_definition_id: Optional[str]
    suspended: bool
    form_key: Optional[str]
    tenant_id: Optional[str]


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
