import logging

from lxml.etree import QName, _Element, fromstring

from .datastructures import (
    DRD,
    Decision,
    DecisionTable,
    DMNIntrospectionResult,
    InputClause,
    OutputClause,
    RequiredDecision,
)

NSMAP = {
    "dmn": "https://www.omg.org/spec/DMN/20191111/MODEL/",
    "camunda": "http://camunda.org/schema/1.0/dmn",
}

logger = logging.getLogger(__name__)


def decision_table_from_xml(node: _Element) -> DecisionTable:
    """
    Build a decision table from
    """
    # id is optional, we currently also don't need references to tables
    table_id = node.get("id", "")

    # extract the inputs
    inputs = [
        input_clause
        for input_element in node.iterfind("dmn:input", namespaces=NSMAP)
        if (input_clause := input_clause_from_xml(input_element))
    ]
    # extract the outputs - the standard says that outputs SHALL have a name if multiple
    # outputs are produced, and SHALL NOT have a name if only a single output is
    # defined. However, Camunda does not enforce this and having a name is pretty
    # useful *actually*. So we only consider named outputs.
    outputs = [
        OutputClause(
            name=name,
            id=output_element.get("id", ""),
            label=output_element.get("label", ""),
            type_ref=output_element.get("typeRef", ""),  # type: ignore
        )
        for output_element in node.iterfind("dmn:output", namespaces=NSMAP)
        if (name := output_element.get("name"))
    ]
    return DecisionTable(id=table_id, inputs=inputs, outputs=outputs)


def input_clause_from_xml(node: _Element) -> InputClause | None:
    """
    Process an input clause node and extract the variable/expression used.
    """
    input_id = node.attrib["id"]
    expression_node = node.find("dmn:inputExpression", namespaces=NSMAP)

    # look up the actual expression
    expression = ""
    if (expression_node is not None) and (
        (text_node := expression_node.find("dmn:text", namespaces=NSMAP)) is not None
    ):
        expression = (text_node.text or "").strip()

    # abort if we can't find an expression
    if not expression:
        logger.debug(
            "Skipping input clause %s, could not find an input expression",
            input_id,
        )
        return None

    return InputClause(
        id=input_id,
        label=node.get("label", ""),
        expression=expression,
        type_ref=expression_node.attrib["typeRef"],  # type: ignore
    )


class Parser:
    """Parse a DMN resource.

    Creating a parser will immediately parse the provided resource, so only create
    instances when there's actual processing required.

    The DMN standard: https://www.omg.org/spec/DMN
    Camunda (at the time of writing) supports parts of the DMN 1.3 spec, see
    https://docs.camunda.org/manual/7.20/reference/dmn/.

    PDF with specification: https://www.omg.org/spec/DMN/1.3/PDF

    Drools also has some solid documentation:
    https://docs.drools.org/latest/drools-docs/drools/DMN/index.html#dmn-drd-components-ref_dmn-models

    The parser only supports local references. We currently do not resolve import
    statements as a naive implementation can lead to security issues (SSR forging etc).
    """

    xml: _Element
    drd: DRD

    def __init__(self, xml: bytes):
        self.xml = fromstring(xml)
        self.drd = self.parse()

    def parse(self) -> DRD:
        """Parse the XML and construct a python DRD object.

        Camunda tends to put all the namespace definitions in the root element, so we
        can grab the nsmap from there.
        """
        decisions_node = self.xml
        tag = QName(decisions_node.tag)
        if not tag.localname == "definitions":
            raise ValueError("The XML file does not appear to be a DMN definition.")

        # Create the top-level resource and parse its contents
        attrs = decisions_node.attrib
        drd = DRD(id=attrs["id"], name=attrs["name"])

        # Find the decisions
        for decision_node in decisions_node.iterfind("dmn:decision", namespaces=NSMAP):
            name = decision_node.attrib["name"]
            decision_id = decision_node.attrib.get("id")
            # the 'id' attribute is apparently optional. Camunda uses this as key, so
            # if we don't know the ID, we cannot target this decision anyway.
            if not decision_id:
                logger.info(
                    "Skipping decision in DRD '%s' without ID, it is not addressable.",
                    drd.id,
                )
                continue

            # does it have a decision table?
            if (
                table_node := decision_node.find("dmn:decisionTable", namespaces=NSMAP)
            ) is None:
                logger.info(
                    "Skipping decision '%s' in DRD '%s' without decision table. "
                    "Currently we don't support other variants of decisions.",
                    decision_id,
                    drd.id,
                )
                continue

            decision_table = decision_table_from_xml(table_node)

            local_references = [
                href[1:]
                for dependency in decision_node.iterfind(
                    "dmn:informationRequirement/dmn:requiredDecision", namespaces=NSMAP
                )
                if (href := dependency.attrib.get("href"))
                # we only support local references, no absolute/relative paths
                if href.startswith("#")
            ]
            required_decisions = [
                RequiredDecision(id_ref=id_ref) for id_ref in local_references
            ]

            drd[decision_id] = Decision(
                id=decision_id,
                name=name,
                decision_table=decision_table,
                required_decisions=required_decisions,
            )

        return drd

    def extract_inputs(self, definition_id: str) -> list[InputClause]:
        """Return the inputs of a decision table.

        Inputs for one table may be outputs provided by a dependency. This takes care
        of only filtering out the inputs that must be provided by the caller to evaluate
        the table.
        """
        decision = self.drd[definition_id]

        all_inputs: list[InputClause] = decision.decision_table.inputs

        # check which outputs are provided and inputs required by decision requirements
        # (these are decision tables that must be evaluated *before* the specified one).
        output_names_from_dependencies: list[str] = []
        for required_decision in decision.required_decisions:
            all_inputs += self.extract_inputs(required_decision.id_ref)
            output_names_from_dependencies += [
                output.name for output in self.extract_outputs(required_decision.id_ref)
            ]

        # XXX: this doesn't catch the cases where the input expression is something like
        # `otherOutput + 10`, for that we'd have to do expression parsing and that's
        # overkill (unless a really good library exists somewhere).
        relevant_inputs = [
            input_clause
            for input_clause in all_inputs
            if input_clause.expression not in output_names_from_dependencies
        ]
        return relevant_inputs

    def extract_outputs(self, definition_id: str) -> list[OutputClause]:
        """Return the outputs of a decision table

        If this table is part of a Decision Requirement Diagram (DRD) and the DRD
        contains multiple decision tables, the tables and their relationship are all
        described in the same XML.

        When you evaluate a decision table with Camunda, if the table has another table
        as a dependency it will be evaluated automatically. Only the outputs of the
        table being run (the 'final' table) will be returned. So if the 'dependency'
        tables have intermediate outputs, these are not returned in the final result.
        """
        decision = self.drd[definition_id]
        assert isinstance(decision, Decision)
        return decision.decision_table.outputs

    def extract_parameters(self, definition_id: str) -> DMNIntrospectionResult:
        return DMNIntrospectionResult(
            inputs=self.extract_inputs(definition_id),
            outputs=self.extract_outputs(definition_id),
        )
