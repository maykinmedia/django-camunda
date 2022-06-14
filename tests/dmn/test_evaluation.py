from django_camunda.dmn import evaluate_dmn


def test_evaluate_by_key(camunda_client, deployed_decision_definition):
    input_vars = {
        "direction": "incoming",
        "port": 443,
    }

    result = evaluate_dmn(
        "firewall_rules", input_values=input_vars, client=camunda_client
    )

    assert result == {"policy": "allow", "reason": "HTTPS traffic"}


def test_evaluate_by_id(camunda_client, deployed_decision_definition):
    input_vars = {
        "direction": "incoming",
        "port": 443,
    }

    result = evaluate_dmn(
        "firewall_rules",
        dmn_id=deployed_decision_definition["id"],
        input_values=input_vars,
        client=camunda_client,
    )

    assert result == {"policy": "allow", "reason": "HTTPS traffic"}
