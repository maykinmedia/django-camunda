from django.contrib import admin
from django.contrib.admin import widgets
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from .fields import ProcessDefinitionField
from .forms import CamundaConfigForm, get_process_definition_choices
from .models import CamundaConfig


@admin.register(CamundaConfig)
class CamundaConfigAdmin(SingletonModelAdmin):
    form = CamundaConfigForm
    fieldsets = (
        (None, {"fields": ("root_url", "rest_api_path")}),
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
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, ProcessDefinitionField):
            kwargs.update(
                {
                    "widget": widgets.AdminRadioSelect(),
                    "choices": get_process_definition_choices(),
                }
            )

        return super().formfield_for_dbfield(db_field, request, **kwargs)
