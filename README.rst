Camunda client for Django
=========================

:Version: 0.11.0
:Source: https://github.com/maykinmedia/django-camunda
:Keywords: camunda, process engine, bpmn

|build-status| |linting| |coverage|

|python-versions| |django-versions| |pypi-version|

Interact with Camunda BPMN processes from Django projects.

.. contents::

.. section-numbering::

Features
========

* Configure Camunda connection parameters from the admin
* Shared Celery tasks
* Domain models as Python objects
* Complex/custom process variable support

Installation
============

Requirements
------------

* Python 3.7 or above
* setuptools 30.3.0 or above
* Django 2.2 or above
* Celery [optional]


Install
-------

.. code-block:: bash

    pip install django-camunda

or with Celery support:

.. code-block:: bash

    pip install django-camunda[celery]

Next, ensure the following apps are installed:

.. code-block:: python

    INSTALLED_APPS = [
        ...,
        "solo",
        "django_camunda",
        ...
    ]

and run migrations:

.. code-block:: bash

    python manage.py migrate

Usage
=====

Configuration
-------------

1. In the admin, navigate to **django-camunda** > **Camunda configuration**
2. Fill out the API connection parameters for your Camunda instance


Using the API client
--------------------

**Built-in API functions**

The module ``django_camunda.api`` contains a number of pre-defined API endpoint
bindings. If what you're looking for does not exist (yet), you can use the low-level
API client (see below).

**Core usage**

The Camunda client class is a wrapper around the
`requests <https://pypi.org/project/requests/>`_ library and as such aims to provide
the same Python interface.

.. code-block:: python

    from django_camunda.client import get_client

    with get_client() as client:
        task = client.get("task/5c793356-24f5-4f82-a5ce-a3cce43b762b")

    ... # do something with the task details


.. |build-status| image:: https://github.com/maykinmedia/django-camunda/workflows/Run%20CI/badge.svg
    :target: https://github.com/maykinmedia/django-camunda/actions?query=workflow%3A%22Run+CI%22
    :alt: Run CI

.. |linting| image:: https://github.com/maykinmedia/django-camunda/workflows/Code%20quality%20checks/badge.svg
    :target: https://github.com/maykinmedia/django-camunda/actions?query=workflow%3A%22Code+quality+checks%22
    :alt: Code linting

.. |coverage| image:: https://codecov.io/gh/maykinmedia/django-camunda/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/django-camunda
    :alt: Coverage status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/django-camunda.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/django-camunda.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/django-camunda.svg
    :target: https://pypi.org/project/django-camunda/
