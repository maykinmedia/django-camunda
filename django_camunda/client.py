"""
Implements a camunda client.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from django.conf import settings
from django.utils.module_loading import import_string

import inflection
import requests

from .models import CamundaConfig

logger = logging.getLogger(__name__)


def get_client_class() -> type:
    client_class = getattr(settings, "CAMUNDA_CLIENT_CLASS", "django_camunda.client.Camunda")
    return import_string(client_class)


class Camunda:
    def __init__(self, config: Optional[CamundaConfig] = None):
        config = config or CamundaConfig.get_solo()
        self.root_url = config.api_root

    def request(self, path: str, method="GET", *args, **kwargs):
        assert not path.startswith("/"), "Provide relative API paths"
        url = urljoin(self.root_url, path)

        # add the API headers, so that Camunda can use the tokens. Essentially
        # we're forwarding Auth
        headers = kwargs.pop("headers", {})
        headers.update(self.get_extra_headers(headers))
        kwargs["headers"] = headers

        json = kwargs.get("json")
        if json:
            self.preprocess_json(json)

        _ref = self.before_request(method, url, *args, **kwargs)

        response = requests.request(method, url, *args, **kwargs)
        response_data = None

        try:
            response.raise_for_status()
            if response.content:
                response_data = response.json()

                if isinstance(response_data, (dict, list)):
                    self.postprocess_response_data(response_data)
            return underscoreize(response_data)
        except Exception:
            try:
                # see if we can grab any extra output
                response_data = response.json()
            except Exception:
                pass
            logger.exception("Error: %r", response_data)
            raise
        finally:
            self.after_request(_ref, response, response_data)

    # HOOKS for subclasses

    def before_request(self, method: str, url: str, *args, **kwargs) -> Any:
        pass

    def after_request(self, ref: Any, response, response_data) -> None:
        pass

    def get_extra_headers(self, headers: dict) -> dict:
        return {}

    def preprocess_json(self, json: dict) -> None:
        pass

    def postprocess_response_data(self, data: Union[list, dict]) -> None:
        pass


def underscoreize(data: Union[List, Dict, str, None]) -> Union[List, Dict, str, None]:
    if isinstance(data, list):
        return [underscoreize(item) for item in data]

    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = inflection.underscore(key)
            new_data[new_key] = underscoreize(value)
        return new_data

    return data
