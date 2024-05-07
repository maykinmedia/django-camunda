"""Data structures to represent DMN elements.

These data structures are created/used by the parser when a ``.dmn`` XML is parsed.

The XML file with the decision definitions contains much more information, we do not
extract everything - only what we actively use is extracted and modelled.
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass, field
from typing import Literal, TypeAlias

CamundaDataType = Literal["string", "integer", "long", "boolean", "date", "double"]


@dataclass
class InputClause:
    # Unique identifier of the decision table input
    id: str
    label: str
    # Specifies how the value of the input clause is generated.
    # We expect FEEL expressions, which is part of the DMN standard.
    # Examples are: `foo` but also `a + b`.
    expression: str
    # The type of the input expression after being evaluated.
    type_ref: CamundaDataType


@dataclass
class OutputClause:
    # all fields are technically optional in the XML, we default to empty strings in
    # those cases.
    id: str
    label: str
    # Used to reference the value of the output.
    name: str
    type_ref: CamundaDataType | Literal[""]


@dataclass
class DecisionTable:
    """
    A single decision table with input and output parameters.
    """

    id: str
    # inputs and outputs are ordered in DMN
    inputs: list[InputClause]
    outputs: list[OutputClause]


@dataclass
class RequiredDecision:
    id_ref: str


@dataclass
class Decision:
    """
    A DMN decision element.

    Camunda support decision tables and literal expressions. We currently do not support
    literal expressions.
    """

    id: str
    name: str
    decision_table: DecisionTable
    required_decisions: Collection[RequiredDecision]


# type alias, because *other* types with an ID can also be recorded.
DRDElement: TypeAlias = Decision  # | DecisionTable


@dataclass
class DRD:
    """
    A single definitions element.

    The definitions element (DRD = definitions resource definition) contains all the
    relevant decisions and their relations.
    """

    id: str
    name: str
    _elements: dict[str, DRDElement] = field(default_factory=dict, repr=False)
    """
    Mapping of element IDs to their element.
    """

    def __contains__(self, item: str | DRDElement) -> bool:
        is_key = isinstance(item, str)
        collection_to_check = (
            self._elements.keys() if is_key else self._elements.values()
        )
        return item in collection_to_check

    def __getitem__(self, element_id: str) -> DRDElement:
        return self._elements[element_id]

    def __setitem__(self, element_id: str, element: DRDElement) -> None:
        self._elements[element_id] = element


@dataclass
class DMNVariable:
    label: str
    type: type
    expression_hint: str = ""


@dataclass
class DMNIntrospectionResult:
    inputs: list[InputClause]
    outputs: list[OutputClause]
