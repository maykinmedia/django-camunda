import pytest

from django_camunda.dmn.parser import Parser


@pytest.mark.assetname("invoiceClassification.dmn")
def test_extract_inputs_decision_table(binary_asset: bytes):
    parser = Parser(xml=binary_asset)

    inputs = parser.extract_inputs("invoiceClassification")

    assert len(inputs) == 2
    amount, category = inputs

    assert amount.label == "Invoice Amount"
    assert amount.expression == "amount"
    assert category.label == "Invoice Category"
    assert category.expression == "invoiceCategory"


@pytest.mark.assetname("invoiceClassification.dmn")
def test_extract_inputs_decision_table_with_dependencies(binary_asset: bytes):
    parser = Parser(xml=binary_asset)

    inputs = parser.extract_inputs("invoice-assign-approver")

    assert len(inputs) == 2
    amount, category = inputs

    assert amount.label == "Invoice Amount"
    assert amount.expression == "amount"
    assert category.label == "Invoice Category"
    assert category.expression == "invoiceCategory"


@pytest.mark.assetname("invoiceClassification.dmn")
def test_extract_outputs_decision_table(binary_asset: bytes):
    parser = Parser(xml=binary_asset)

    outputs = parser.extract_outputs("invoiceClassification")

    assert len(outputs) == 1
    assert outputs[0].label == "Classification"
    assert outputs[0].name == "invoiceClassification"


@pytest.mark.assetname("invoiceClassification.dmn")
def test_extract_outputs_decision_table_with_dependencies(binary_asset: bytes):
    parser = Parser(xml=binary_asset)

    outputs = parser.extract_outputs("invoice-assign-approver")

    assert len(outputs) == 1
    assert outputs[0].label == "Approver Group"
    assert outputs[0].name == "result"


@pytest.mark.assetname("multi-drd.dmn")
def test_introspect_multi_table_drds_with_dependencies(binary_asset: bytes):
    """
    Assert that the parser resolves `requiredDecision` nodes.
    """
    parser = Parser(binary_asset)

    leaf_inputs = parser.extract_inputs("multi-2")

    input_expressions = {x.expression for x in leaf_inputs}
    assert input_expressions == {"a", "a + b", "reference"}


@pytest.mark.assetname("multi-drd.dmn")
def test_get_full_introspection_result(binary_asset: bytes):
    parser = Parser(binary_asset)

    parameters = parser.extract_parameters("multi-2")

    assert len(parameters.inputs) == 3
    assert len(parameters.outputs) == 1
