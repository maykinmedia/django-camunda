from typing import List

from lxml.etree import fromstring

from .datastructures import DMNIntrospectionResult
from .types import DMNInputParameter, DMNOutputParameter
from .utils import (
    extract_decision_definition_inputs,
    extract_decision_definition_outputs,
)


class Parser:
    def __init__(self, xml: bytes):
        self.xml = fromstring(xml)

    def extract_inputs(self, definition_id: str) -> List[DMNInputParameter]:
        """
        Return the inputs of a decision table

        A decision table can have one or more required decisions which it depends on.
        Here we recurse to see which initial inputs are needed to evaluate a decision table that might depend on other
        tables.
        """
        return extract_decision_definition_inputs(self.xml, definition_id)

    def extract_outputs(self, definition_id: str) -> List[DMNOutputParameter]:
        """Return the outputs of a decision table

        If this table is part of a Decision Requirement Diagram (DRD) and the DRD contains multiple decision tables, the
        tables and their relationship are all described in the same XML.

        When you evaluate a decision table with Camunda, if the table has another table as a dependency it will be
        evaluated automatically. Only the outputs of the table being run (the 'final' table) will be returned.
        So if the 'dependency' tables have intermediate outputs, these are not returned in the final result.
        """
        return extract_decision_definition_outputs(self.xml, definition_id)

    def extract_parameters(self, definition_id: str) -> DMNIntrospectionResult:
        return DMNIntrospectionResult(
            inputs=self.extract_inputs(definition_id),
            outputs=self.extract_outputs(definition_id),
        )
