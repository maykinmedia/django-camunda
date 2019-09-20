from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import CamundaConfig


@admin.register(CamundaConfig)
class CamundaConfigAdmin(SingletonModelAdmin):
    pass
