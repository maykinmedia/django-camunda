import base64
from itertools import groupby
from typing import List, Tuple, Union
from xml.etree.ElementTree import Element

from django import forms
from django.utils.translation import gettext_lazy as _

from .api import get_process_definitions
from .constants import LATEST
from .models import CamundaConfig

Choice = Tuple[str, str]


class CamundaConfigForm(forms.ModelForm):
    basic_auth_username = forms.CharField(
        label=_("Username"),
        required=False,
        help_text=_("Username to authenticate against the Camunda API."),
    )

    basic_auth_password = forms.CharField(
        label=_("Password"),
        required=False,
        help_text=_("Password to authenticate against the Camunda API."),
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CamundaConfig
        fields = (
            "root_url",
            "rest_api_path",
            "basic_auth_username",
            "basic_auth_password",
        )

    def __init__(self, *args, **kwargs):
        config = kwargs.get("instance")
        if config is not None:
            creds = self.set_creds_from_header(config)
            if creds is not None:
                kwargs.setdefault("initial", {})
                kwargs["initial"].update(creds)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        self.set_basic_auth_header()

    def set_basic_auth_header(self):
        username = self.cleaned_data.get("basic_auth_username")
        password = self.cleaned_data.get("basic_auth_password")
        if not (username and password):
            return

        basic_auth = f"{username}:{password}"
        b64 = base64.b64encode(basic_auth.encode()).decode()
        self.instance.auth_header = f"Basic {b64}"

    def set_creds_from_header(self, config: CamundaConfig) -> Union[dict, None]:
        if not config.auth_header.startswith("Basic "):
            return

        prefix, b64 = config.auth_header.split(" ", 1)
        decoded = base64.b64decode(b64).decode()
        username, password = decoded.split(":", 1)
        return {"basic_auth_username": username, "basic_auth_password": password}


def get_process_definition_choices() -> List[Tuple[str, List[Choice]]]:
    definitions = get_process_definitions()

    definitions = sorted(definitions, key=lambda d: (d.key, -d.version))
    def_by_key = groupby(definitions, lambda x: x.key)

    def get_latest_choice(key: str):
        value = f"{key}:{LATEST}"
        return (value, _("latest"))

    choices = [
        (
            key,
            [get_latest_choice(key)]
            + [
                (definition.id, _("version {d.version}").format(d=definition))
                for definition in definitions
            ],
        )
        for key, definitions in def_by_key
    ]
    return choices


class ProcessDefinitionChoicesField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.pop("max_length", None)
        kwargs.setdefault("choices", get_process_definition_choices)
        super().__init__(*args, **kwargs)


FIELD_TYPE_MAP = {
    "enum": forms.ChoiceField,
    "string": forms.CharField,
    "long": forms.IntegerField,
    "boolean": forms.BooleanField,
    "date": forms.DateTimeField,
}


def formfield_from_xml(definition: Element) -> Tuple[str, forms.Field]:
    name = definition.attrib["id"]
    label = definition.attrib.get("label", "")
    default = definition.attrib.get("defaultValue")

    field_type = definition.attrib["type"]
    if field_type not in FIELD_TYPE_MAP:
        raise NotImplementedError(f"Unknown field type '{field_type}'")

    field_class = FIELD_TYPE_MAP[field_type]

    field_kwargs = {
        "label": label,
        "initial": default,
    }

    if field_type == "enum":
        field_kwargs["choices"] = [
            (value.attrib["id"], value.attrib["name"])
            for value in definition.getchildren()
        ]
        field_kwargs["widget"] = forms.RadioSelect

    return name, field_class(required=True, **field_kwargs)
