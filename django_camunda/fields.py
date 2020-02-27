from django.db import models
from django.utils.translation import gettext_lazy as _

from .forms import ProcessDefinitionChoicesField


class ProcessDefinitionField(models.CharField):
    def __init__(self, *args, **kwargs):
        # See https://github.com/camunda/camunda-bpm-platform/blob/master/engine/src/
        # main/resources/org/camunda/bpm/engine/db/create/activiti.mysql.create.engine.sql#L134
        # for FK VARCHAR(64) reference
        kwargs.setdefault("max_length", 64)
        kwargs.setdefault("help_text", _("ID of the process definition in Camunda"))
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"form_class": ProcessDefinitionChoicesField}
        defaults.update(**kwargs)
        return super().formfield(**defaults)
