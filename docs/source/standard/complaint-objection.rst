
.. include:: defs.hrst

.. index:: ComplaintObjection, dispute

.. _complaint-objection:

ComplaintObjection
==================

Schema
------

:id:
    uid, auto-generated

    Id of objection

:title:
    string, required

    Title of objection

:description:
    string, required

    Description of objection

:relatesTo:
    string, required

    Type of related element.
    Possible values are:

    * `tender`
    * `lot`
    * `requirement`
    * `requirement_response`
    * `award`
    * `qualification`
    * `cancellation`

:relatedItem:
    string, required

    The path in the tender to this element.

:classification:
    :ref:`complaint-objection-classification`

:requestedRemedies:
    List of :ref:`complaint-objection-requested-remedy` objects

:arguments:
    List of :ref:`complaint-objection-argument` objects

