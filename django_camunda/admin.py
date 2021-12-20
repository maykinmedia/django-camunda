from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from .fields import ProcessDefinitionField
from .forms import CamundaConfigForm, get_process_definition_choices
from .models import CamundaConfig


@admin.register(CamundaConfig)
class CamundaConfigAdmin(SingletonModelAdmin):
    form = CamundaConfigForm
    fieldsets = (
        (None, {"fields": ("root_url", "rest_api_path", "enabled")}),
        (
            _("Auth"),
            {
                "fields": (
                    ("basic_auth_username", "basic_auth_password"),
                    ("auth_header",),
                )
            },
        ),
    )
    readonly_fields = ("auth_header",)


class CamundaFieldsMixin:
    def _is_enabled(self, request) -> bool:
        # cache on the request, as model admin instances persist across requests
        if not hasattr(request, "_camunda_config"):
            request._camunda_config = CamundaConfig.get_solo()
        return request._camunda_config.enabled

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if self._is_enabled(request) and isinstance(db_field, ProcessDefinitionField):
            kwargs.update(
                {"widget": forms.Select, "choices": get_process_definition_choices()}
            )

        return super().formfield_for_dbfield(db_field, request, **kwargs)
