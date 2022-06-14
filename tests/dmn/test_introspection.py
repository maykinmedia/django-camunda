from dataclasses import asdict

from django_camunda.dmn import introspect_dmn


def test_introspect_by_key(camunda_client, deployed_decision_definition):
    result = introspect_dmn("firewall_rules", client=camunda_client)

    assert asdict(result) == {
        "inputs": [
            {
                "label": "Direction",
                "type": str,
                "expression_hint": "direction",
            },
            {
                "label": "Port number",
                "type": int,
                "expression_hint": "port",
            },
            {
                "label": "Camunda variable",
                "type": str,
                "expression_hint": "someVar",
            },
            {
                "label": "",
                "type": str,
                "expression_hint": "",
            },
        ],
        "output": {
            "policy": {
                "label": "Policy",
                "type": str,
                "expression_hint": "",
            },
            "reason": {
                "label": "Reason",
                "type": str,
                "expression_hint": "",
            },
        },
    }
