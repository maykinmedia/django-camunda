# Generated by Django 2.2.5 on 2020-05-25 04:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("django_camunda", "0003_auto_20200227_1552")]

    operations = [
        migrations.AddField(
            model_name="camundaconfig",
            name="enabled",
            field=models.BooleanField(
                default=True,
                help_text="Global flag to enable/disable Camund integration.",
                verbose_name="enabled",
            ),
        )
    ]
