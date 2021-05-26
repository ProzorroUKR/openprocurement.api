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

    Possible values are:

    * `executionOfWorks`
    * `deliveryOfGoods`
    * `submittingServices`
    * `signingTheContract`
    * `submissionDateOfApplications`
    * `dateOfInvoicing`
    * `endDateOfTheReportingPeriod`
    * `anotherEvent`

:description:
    string, required if title == `anotherEvent`

:type:
    string, required

    The only possible value is:

    * `financing`

:code:
    string, required

    Possible values are:

    * `prepayment`
    * `postpayment`

:percentage:
    float, required, 0..100

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

:description:
    string, required if title == `anotherEvent`

:type:
    string, required

    The only possible value is:

    * `activation`
    * `ban`
    * `disqualification`
    * `terminated`


:dueDate:
    string, :ref:`date`, required

:documents:
    List of :ref:`document` objects

:dateModified:
    string, :ref:`date`, auto-generated, read-only

    The date of milestone change.


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
