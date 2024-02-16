Changelog
=========

0.14.0 (2024-02-16)
-------------------

* Updated Github actions and Tox to test django 4.1 and 4.2 and dropped python 3.7.
* Removed typing extension dependency (was only needed for python 3.7).
* Replaced defusedxml.lxml module with lxml.
* Added parser for XML of Camunda decision definitions.


0.13.0 (2023-02-02)
-------------------

* Fixed serialize utility for ``OrderedDict``
* Formatted code with latest black version
* Disable browser autocomplete for password field in config admin

0.12.0 (2022-06-14)
-------------------

* Added changelog
* Dropped supported for Django 2.2
* Added initial DMN functionality

    * Implement evaluating a DMN table by ID or key
    * Implement introspecing a DMN table by ID or key

* Exposed types
* Improved type hints
