from pathlib import Path

from django_camunda.dmn.parser import Parser

TEST_DRD_XML = (Path(__file__).parent / "data" / "drd.xml").read_bytes()


def test_extract_inputs_decision_table():
    parser = Parser(xml=TEST_DRD_XML)

    inputs = parser.extract_inputs("invoiceClassification")

    assert len(inputs) == 2
    assert inputs[0]["label"] == "Invoice Amount"
    assert inputs[0]["expression"] == "amount"
    assert inputs[1]["label"] == "Invoice Category"
    assert inputs[1]["expression"] == "invoiceCategory"


def test_extract_inputs_decision_table_with_dependencies():
    parser = Parser(xml=TEST_DRD_XML)

    inputs = parser.extract_inputs("invoice-assign-approver")

    assert len(inputs) == 2
    assert inputs[0]["label"] == "Invoice Amount"
    assert inputs[0]["expression"] == "amount"
    assert inputs[1]["label"] == "Invoice Category"
    assert inputs[1]["expression"] == "invoiceCategory"


def test_extract_outputs_decision_table():
    parser = Parser(xml=TEST_DRD_XML)

    outputs = parser.extract_outputs("invoiceClassification")

    assert len(outputs) == 1
    assert outputs[0]["label"] == "Classification"
    assert outputs[0]["name"] == "invoiceClassification"


def test_extract_outputs_decision_table_with_dependencies():
    parser = Parser(xml=TEST_DRD_XML)

    outputs = parser.extract_outputs("invoice-assign-approver")

    assert len(outputs) == 1
    assert outputs[0]["label"] == "Approver Group"
    assert outputs[0]["name"] == "result"
