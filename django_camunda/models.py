from urllib.parse import urljoin

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel


class CamundaConfig(SingletonModel):
    root_url = models.URLField(
        _("camunda root"),
        help_text=_(
            "Root URL where camunda is installed. The REST api "
            "path is appended to this."
        ),
        default="http://localhost:12018/gemeente-utrecht/camunda/",
    )
    rest_api_path = models.CharField(
        _("REST api path"), max_length=255, default="engine-rest"
    )

    class Meta:
        verbose_name = _("Camunda configuration")

    def __str__(self):
        return self.api_root

    def clean(self):
        from .client import get_client_class

        client = get_client_class()(config=self)
        try:
            client.request("version")
        except Exception as exc:
            raise ValidationError(
                _(
                    "Invalid API root '{root}', got error {error} while checking the "
                    "version endpoint."
                ).format(root=self.api_root, error=exc)
            )

    def save(self, *args, **kwargs):
        if self.rest_api_path.startswith("/"):
            self.rest_api_path = self.rest_api_path[1:]

        if not self.rest_api_path.endswith("/"):
            self.rest_api_path = f"{self.rest_api_path}/"

        super().save(*args, **kwargs)

    @property
    def api_root(self) -> str:
        assert not self.rest_api_path.startswith("/")
        assert self.rest_api_path.endswith("/")
        return urljoin(self.root_url, self.rest_api_path)
