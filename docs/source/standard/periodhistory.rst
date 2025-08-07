.. _PeriodChangeHistory:

PeriodChangeHistory
====================

Schema
------

:id:
    uid, auto-generated

:cause:
    string, required

    The cause, why qualificationPeriod is being changed.
    Possible values for causes in `framework period change causes <https://prozorroukr.github.io/standards/codelists/framework/framework_period_change_causes.json>`_ dictionaries.

:causeDescription:
    string, required

    The description of cause, why qualificationPeriod is being changed.

:prevPeriodEndDate:
    string, required

    Previous framework `qualificationPeriod.endDate`

:newPeriodEndDate:
    string, required

    New framework `qualificationPeriod.endDate`

:date:
    string, :ref:`Date`, auto-generated, read-only

    The date of the period changes.

:documents:
    List of :ref:`Document` objects
