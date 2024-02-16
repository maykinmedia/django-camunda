from django_camunda.dmn import get_dmn_parser


def test_introspect_by_key(camunda_client, deployed_decision_definition):
    parser = get_dmn_parser("firewall_rules", client=camunda_client)
    inputs = parser.extract_inputs("firewall_rules")
    outputs = parser.extract_outputs("firewall_rules")

    assert inputs == [
        {
            "label": "Direction",
            "id": "Input_1",
            "type_ref": "string",
            "expression": "direction",
            "input_variable": "",
        },
        {
            "label": "Port number",
            "id": "InputClause_1cn8gp3",
            "type_ref": "integer",
            "expression": "port",
            "input_variable": "",
        },
        {
            "label": "Camunda variable",
            "id": "InputClause_1f09wt8",
            "type_ref": "string",
            "expression": "",
            "input_variable": "someVar",
        },
        {
            "label": "",
            "id": "InputClause_0xg43gn",
            "type_ref": "string",
            "expression": "",
            "input_variable": "",
        },
    ]
    assert outputs == [
        {
            "id": "Output_1",
            "label": "Policy",
            "type_ref": "string",
            "name": "policy",
        },
        {
            "id": "OutputClause_0lzmnio",
            "label": "Reason",
            "type_ref": "string",
            "name": "reason",
        },
    ]
