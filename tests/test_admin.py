from django.urls import reverse

import pytest

from django_camunda.models import CamundaConfig


@pytest.mark.django_db
def test_enter_basic_auth(requests_mock, django_app, admin_user):
    config = CamundaConfig.get_solo()
    assert config.auth_header == ""
    django_app.set_user(admin_user)
    requests_mock.get(
        "https://camunda.example.com/engine-rest/version",
        status_code=200,
        json={"version": "7.11.0"},
    )
    admin_url = reverse("admin:django_camunda_camundaconfig_changelist")

    change_page = django_app.get(admin_url)

    change_page.forms["camundaconfig_form"]["basic_auth_username"] = "dummy"
    change_page.forms["camundaconfig_form"]["basic_auth_password"] = "secret"
    change_page.forms["camundaconfig_form"].submit().follow()

    config.refresh_from_db()
    assert config.auth_header == "Basic ZHVtbXk6c2VjcmV0"

    auth = requests_mock.last_request.headers["Authorization"]
    assert auth == "Basic ZHVtbXk6c2VjcmV0"


@pytest.mark.django_db
def test_select_process_definition(requests_mock, django_app, admin_user):
    django_app.set_user(admin_user)
    requests_mock.get(
        "https://camunda.example.com/engine-rest/process-definition",
        json=[
            {
                "id": "dummy:1",
                "category": "http://bpmn.io/schema/bpmn",
                "deployment_id": "1f8bae6e-53e7-11ea-b0b2-7ee96954906c",
                "description": None,
                "diagram": None,
                "history_time_to_live": None,
                "key": "dummy",
                "name": "Dummy",
                "resource": "dummy.bpmn",
                "startable_in_tasklist": True,
                "suspended": False,
                "tenant_id": None,
                "version": 1,
                "version_tag": None,
            },
            {
                "id": "dummy:2",
                "category": "http://bpmn.io/schema/bpmn",
                "deployment_id": "f0bc1357-831b-40a5-859b-21306db1cf08",
                "description": None,
                "diagram": None,
                "history_time_to_live": None,
                "key": "dummy",
                "name": "Dummy",
                "resource": "dummy.bpmn",
                "startable_in_tasklist": True,
                "suspended": False,
                "tenant_id": None,
                "version": 2,
                "version_tag": None,
            },
        ],
    )
    admin_url = reverse("admin:testapp_camunda_add")
    add_page = django_app.get(admin_url)
    field = field = add_page.forms["camunda_form"]["process_definition"]

    try:
        field.select("dummy:2")
    except Exception:
        pytest.fail("Missing option dummy:2")

    with pytest.raises(ValueError):
        field.select("foo")
