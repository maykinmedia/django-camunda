from django.db import models

from django_camunda.fields import ProcessDefinitionField


class Camunda(models.Model):
    process_definition = ProcessDefinitionField(blank=True)
