from dataclasses import dataclass
from typing import List

from .types import DMNInputParameter, DMNOutputParameter


@dataclass
class DMNVariable:
    label: str
    type: type
    expression_hint: str = ""


@dataclass
class DMNIntrospectionResult:
    inputs: List[DMNInputParameter]
    outputs: List[DMNOutputParameter]
