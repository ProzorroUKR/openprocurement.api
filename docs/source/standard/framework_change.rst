.. _FrameworkChange:

FrameworkChange
=================

Schema
------

:id:
    uid, auto-generated

:rationaleType:
    string, required

    Reason for framework change

    Possible values for reasons in `framework period change causes <https://prozorroukr.github.io/standards/codelists/framework/framework_period_change_causes.json>`_ dictionaries.

:rationale:
    string, multilingual, required

    The description of reason, why framework should be changed.

:modifications:
    List of :ref:`FrameworkChangeModifications` objects

:previous:
    List of :ref:`FrameworkChangeModifications` objects with values of framework before change.

:date:
    string, :ref:`Date`, auto-generated, read-only

    The date of the period changes.

:dateModified:
    string, :ref:`date`, auto-generated

:documents:
    List of :ref:`Document` objects


.. _FrameworkChangeModifications:

FrameworkChangeModifications
=============================

Schema
------

:qualificationPeriod:
   :ref:`period`, required

   Period when submissions can be qualified. At least `endDate` has to be provided.
