.. index:: Milestone

.. _milestone:

Milestone
=========

Schema
------

:id:
    uid, auto-generated

:title:
    string, required

    Possible values should be from `milestones <https://prozorroukr.github.io/standards/codelists/milestones/title.json>`__ dictionaries.

:description:
    string, required if title == `anotherEvent`

:type:
    string, required

    The only possible value is:

    * `financing`
    * `delivery`

:code:
    string, required

    Possible values should be from `milestones <https://prozorroukr.github.io/standards/codelists/milestones/code.json>`_ dictionaries.

:percentage:
    float, 0..100

    Sum of all tender (or lot) milestones should be 100

:duration:
    :ref:`Duration` object, required

:sequenceNumber:
    integer, required, non negative

:relatedLot:
    uid

    Id of related :ref:`lot`.


Milestone in :ref:`frameworks_electroniccatalogue`
==================================================

Schema
------

:id:
    uid, auto-generated

:type:
    string, required

    The only possible value is:

    * `activation`
    * `ban`

:status:
    string

    The only possible value is:

    * `scheduled`
    * `met`
    * `notMet`
    * `partiallyMet`

:dueDate:
    string, :ref:`date`

:documents:
    List of :ref:`document` objects

:dateModified:
    string, :ref:`date`, auto-generated, read-only

    The date of milestone change.

:dateMet:
    string, :ref:`date`


.. _ContractMilestone:

ContractMilestone
=================

Schema
------

:id:
    uid, auto-generated

:title:
    string, required

    Possible values should be from `milestones <https://prozorroukr.github.io/standards/codelists/milestones/title.json>`__ dictionaries.

:description:
    string, required if title == `anotherEvent`

:type:
    string, required

    The only possible value is:

    * `financing`
    * `delivery`

:code:
    string, required

    Possible values should be from `milestones <https://prozorroukr.github.io/standards/codelists/milestones/code.json>`_ dictionaries.

:percentage:
    float, 0..100

    Sum of all tender (or lot) milestones should be 100

:duration:
    :ref:`Duration` object, required

:sequenceNumber:
    integer, required, non negative

:relatedLot:
    uid

    Id of related :ref:`lot`.

:status:
    string

    The only possible value is:

    * `scheduled`

:dateMet:
    string, :ref:`date`

.. _Duration:

Duration
========

Schema
------

:days:
    integer, required, positive

:type:
    string, required

    Possible values are:

    * `working`
    * `banking`
    * `calendar`
