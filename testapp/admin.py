from django.contrib import admin

from django_camunda.admin import CamundaFieldsMixin

from .models import Camunda


@admin.register(Camunda)
class CamundaAdmin(CamundaFieldsMixin, admin.ModelAdmin):
    pass
