import base64
import os
from pathlib import Path
from urllib.parse import urlparse

import pytest

from django_camunda.client import get_client
from django_camunda.models import CamundaConfig

FILES_DIR = Path(__file__).parent / "files"

CAMUNDA_USER = os.getenv("CAMUNDA_USER", "demo")
CAMUNDA_PASSWORD = os.getenv("CAMUNDA_PASSWORD", "demo")
CAMUNDA_API_BASE_URL = os.getenv(
    "CAMUNDA_API_BASE_URL", "http://localhost:8080/engine-rest/"
)


@pytest.fixture(scope="module")
def camunda_client():
    parsed = urlparse(CAMUNDA_API_BASE_URL)
    basic_auth = f"{CAMUNDA_USER}:{CAMUNDA_PASSWORD}"
    b64 = base64.b64encode(basic_auth.encode()).decode()
    config = CamundaConfig(
        root_url=f"{parsed.scheme}://{parsed.netloc}",
        rest_api_path=parsed.path[1:],  # cut off leading slash
        auth_header=f"Basic {b64}",
    )
    return get_client(config=config)


@pytest.fixture
def binary_asset(request) -> bytes:
    marker = request.node.get_closest_marker("assetname")
    assert marker
    filename = marker.args[0]
    assert isinstance(filename, str)
    file = FILES_DIR / filename
    return file.read_bytes()


@pytest.fixture
def deployed_decision_definition(camunda_client) -> dict:
    dmn = FILES_DIR / "decision_def.dmn"
    with open(dmn, "rb") as infile:
        response = camunda_client.post(
            "deployment/create",
            data={
                "deployment-name": "pytest decision table",
                "enable-duplicate-filtering": "true",
                "deployment-source": "test-suite django-camunda",
            },
            files={"decision_def.dmn": infile},
        )
        # if the resource already exists, the decision definitions are not returned by
        # Camunda, so fetch them in a separate call
        decision_definitions = camunda_client.get(
            "decision-definition", {"deploymentId": response["id"]}
        )
        assert len(decision_definitions) == 1

    dd = decision_definitions[0]
    return {
        "id": dd["id"],
        "key": dd["key"],
        "name": dd["name"],
        "version": dd["version"],
    }
