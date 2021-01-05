
.. include:: defs.hrst

.. index:: Submission
.. _submission:

Submission
==========

Schema
------

:tenderers:
   List of :ref:`BusinessOrganization` objects

:frameworkID:
   string

   The framework identifier.

:qualificationID:
   string, auto-generated, read-only

   The qualification identifier.

:submissionType:
    string, auto-generated from framework model with id frameworkID

    :`electronicCatalogue`:
        Submission for electronic catalog process

:date:
    string, :ref:`date`, auto-generated

:documents:
   List of :ref:`document` objects

   |ocdsDescription|
   All documents and attachments related to the submission.

:datePublished:
    string, :ref:`date`, auto-generated

:dateModified:
    string, :ref:`date`, auto-generated

:owner:
    string, auto-generated

:status:
   string

   :`draft`:
      If :code:`submissionType` is :code:`electronicCatalogue`, then in this status any fields of submission can be changed(besides :code:`qualificationID`).
   :`active`:
      If :code:`submissionType` is :code:`electronicCatalogue`, in this status creates qualification object and set :code:`qualificationID`.
   :`deleted`:
      Terminal status.
   :`complete`:
      Complete submission.

   Status of the Submission.

:revisions:
   List of :ref:`revision` objects, auto-generated

   Historical changes to Submission object properties.
