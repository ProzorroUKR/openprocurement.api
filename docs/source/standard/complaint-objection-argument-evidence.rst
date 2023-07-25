
.. include:: defs.hrst

.. index:: ComplaintObjectionArgumentEvidence, dispute

.. _complaint-objection-argument-evidence:

ComplaintObjectionArgumentEvidence
===================================

Schema
------

:id:
    uid, auto-generated

    Id of the evidence

:type:
    string, required

    Type of the evidence.
    Possible values are:

    * `external`
    * `internal`

:title:
    string, required

    Title of the evidence

:description:
    string, required

    Description of the evidence

:documents:
   List of :ref:`document` objects
