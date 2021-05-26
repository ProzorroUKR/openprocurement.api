
.. index:: Observation
.. _observation:

Observation
===========

Schema
------

:id:
    uid, auto-generated

:period:
    :ref:`period`, required

:measure:
    string

    Observation measure.

:unit:
    :ref:`ObservationUnit` object

:dimensions:
    List of :ref:`Dimension` objects

    Subject or characteristic to which observation obey.

:notes:
    string

    Metric notes.

:relatedImplementationMilestone:
    :ref:`MilestoneReference` object

    Link to :ref:`MilestoneReference` for metric.
