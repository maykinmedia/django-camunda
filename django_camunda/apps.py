from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoCamundaConfig(AppConfig):
    name = "django_camunda"
    verbose_name = _("Camunda")
