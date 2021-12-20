"""
Implements a camunda client.
"""
import logging
from typing import Any, Optional, Union
from urllib.parse import urljoin

from django.conf import settings
from django.utils.module_loading import import_string

import requests

from .models import CamundaConfig
from .utils import underscoreize

logger = logging.getLogger(__name__)


def get_client_class() -> type:
    client_class = getattr(
        settings, "CAMUNDA_CLIENT_CLASS", "django_camunda.client.Camunda"
    )
    return import_string(client_class)


def get_client(*args, **kwargs):
    client_class = get_client_class()
    return client_class(*args, **kwargs)


class Camunda:
    def __init__(self, config: Optional[CamundaConfig] = None):
        self.config = config or CamundaConfig.get_solo()
        self.root_url = self.config.api_root
        self.session = None

    def __enter__(self):
        if self.session is None:
            self.session = requests.Session()
        return self

    def __exit__(self, *args):
        self.session.__exit__(*args)

    @property
    def auth(self) -> dict:
        if not self.config.auth_header:
            return {}
        return {"Authorization": self.config.auth_header}

    def request(self, path: str, method="GET", *args, **kwargs):
        assert not path.startswith("/"), "Provide relative API paths"
        url = urljoin(self.root_url, path)

        do_underscoreize = kwargs.pop("underscoreize", True)

        # add the API headers, so that Camunda can use the tokens. Essentially
        # we're forwarding Auth
        headers = kwargs.pop("headers", {})
        headers.update(self.auth)
        headers.update(self.get_extra_headers(headers))
        kwargs["headers"] = headers

        json = kwargs.get("json")
        if json:
            self.preprocess_json(json)

        _ref = self.before_request(method, url, *args, **kwargs)

        # ensure this works both with client as context manager or as one-off session
        session = self.session or requests
        response = session.request(method, url, *args, **kwargs)
        response_data = None

        try:
            response.raise_for_status()
            if response.content:
                # json is the default Content-Type
                content_type = response.headers.get("Content-Type", "application/json")
                if content_type.startswith("application/json"):
                    response_data = response.json()

                    if isinstance(response_data, (dict, list)):
                        self.postprocess_response_data(response_data)

                    if do_underscoreize:
                        response_data = underscoreize(response_data)
                else:
                    # binary content
                    response_data = response.content

            return response_data
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

    def get(self, path: str, params=None, *args, **kwargs):
        return self.request(path, method="GET", params=params, *args, **kwargs)

    def post(self, path: str, data=None, json=None, *args, **kwargs):
        return self.request(path, method="POST", data=data, json=json, *args, **kwargs)

    def put(self, path: str, data=None, *args, **kwargs):
        return self.request(path, method="PUT", data=data, *args, **kwargs)

    def patch(self, path: str, data=None, *args, **kwargs):
        return self.request(path, method="PATCH", data=data, *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self.request(path, method="DELETE", *args, **kwargs)

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
