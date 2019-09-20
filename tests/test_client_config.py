from django.core.exceptions import ValidationError

import pytest
import requests_mock

from django_camunda.models import CamundaConfig


def test_config_validation():
    config = CamundaConfig(
        root_url="https://some.camunda.nl", rest_api_path="engine-rest/"
    )

    with requests_mock.Mocker() as m:
        m.register_uri(
            "GET",
            "https://some.camunda.nl/engine-rest/version",
            json={"version": "7.11.0"},
        )
        config.clean()


def test_config_validation_failure():
    config = CamundaConfig(
        root_url="https://some.camunda.nl", rest_api_path="engine-rest/"
    )

    with requests_mock.Mocker() as m:
        m.register_uri(
            "GET",
            "https://some.camunda.nl/engine-rest/version",
            json={"error": "BOOM"},
            status_code=500,
        )

        with pytest.raises(ValidationError):
            config.clean()
