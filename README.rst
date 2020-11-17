

.. django-camunda documentation master file, created by startproject.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-camunda's documentation!
=================================================

:Version: 0.9.6
:Source: https://github.com/maykinmedia/django-camunda
:Keywords: camunda, process engine, bpmn
:PythonVersion: 3.7

|build-status| |requirements| |coverage|

|python-versions| |django-versions| |pypi-version|

<One liner describing the project>

.. contents::

.. section-numbering::

Features
========

* Admin model for Camunda configuration
* Shared Celery tasks
* Domain models as Python objects
* Complex/custom process variable support

Installation
============

Requirements
------------

* Python 3.7 or above (3.6 probably also works with the package ``dataclasses``)
* setuptools 30.3.0 or above
* Django 2.2 or above
* Celery


Install
-------

.. code-block:: bash

    pip install django-camunda

Next, ensure the following apps are installed:

.. code-block:: python

    INSTALLED_APPS = [
        ...,
        "solo",
        "django_camunda",
        ...
    ]

Usage
=====

TODO


.. |build-status| image:: https://travis-ci.org/maykinmedia/django-camunda.svg?branch=develop
    :target: https://travis-ci.org/maykinmedia/django-camunda

.. |requirements| image:: https://requires.io/github/maykinmedia/django-camunda/requirements.svg?branch=develop
    :target: https://requires.io/github/maykinmedia/django-camunda/requirements/?branch=develop
    :alt: Requirements status

.. |coverage| image:: https://codecov.io/gh/maykinmedia/django-camunda/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/django-camunda
    :alt: Coverage status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/django-camunda.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/django-camunda.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/django-camunda.svg
    :target: https://pypi.org/project/django-camunda/
