import os

import pytest

from django_camunda.dmn import evaluate_dmn

CAMUNDA_USER = os.getenv("CAMUNDA_USER", "demo")
CAMUNDA_PASSWORD = os.getenv("CAMUNDA_PASSWORD", "demo")


def test_evaluate_by_key(camunda_client, deployed_decision_definition):
    import bpdb

    bpdb.set_trace()
    pass
