
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
    string

    Description of objection

:relatesTo:
    string, required

    Type of related element.
    Possible values are:

    * `tender`
    * `lot`
    * `award`
    * `qualification`
    * `cancellation`

:relatedItem:
    string, required

    The id of related element.

:classification:
    :ref:`complaint-objection-classification`

:requestedRemedies:
    List of :ref:`complaint-objection-requested-remedy` objects

:arguments:
    List of :ref:`complaint-objection-argument` objects

:sequenceNumber:
    integer, non negative

