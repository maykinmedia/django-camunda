from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DMNVariable:
    label: str
    type: type
    expression_hint: str = ""


@dataclass
class IntrospectionResult:
    inputs: List[DMNVariable]
    output: Dict[str, DMNVariable]
