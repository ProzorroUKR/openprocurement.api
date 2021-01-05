
.. include:: defs.hrst

.. index:: FrameworkQualification
.. _framework_qualification:

Qualification
=============

Schema
------

:frameworkID:
   string, auto-generated, read-only

   The framework identifier.

:submissionID:
   string, auto-generated, read-only

   The submission identifier.

:qualificationType:
    string, auto-generated, read-only

    :`electronicCatalogue`:
        Qualification for electronic catalog process

:date:
    string, :ref:`date`, auto-generated

:documents:
   List of :ref:`document` objects

   |ocdsDescription|
   All documents and attachments related to the qualification.

:dateModified:
    string, :ref:`date`, auto-generated

:status:
   string

   :`pending`:
      If :code:`qualificationType` is :code:`electronicCatalogue`, then in this status can be uploaded documents and changed status.
   :`active`:
      If :code:`qualificationType` is :code:`electronicCatalogue`, in this status creates qualification object and set :code:`qualificationID`.
   :`unsuccessful`:
      Terminal status.

   Status of the Qualification.

:revisions:
   List of :ref:`revision` objects, auto-generated

   Historical changes to Qualification object properties.
