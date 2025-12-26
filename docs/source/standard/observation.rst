
.. index:: Observation
.. _observation:

Observation
===========

Schema
------

:id:
    uid, генерується автоматично

:period:
    :ref:`period`, обов'язково

:measure:
    рядок

    Вимір Observation

:unit:
    Об'єкт :ref:`Unit`

:dimensions:
    Список об'єктів :ref:`Dimension`

    Предмет або характеристика на яку посилається Observation.

:notes:
    рядок

    Примітки метрики.

:relatedImplementationMilestone:
    Об'єкт :ref:`MilestoneReference`.

    Посилання на :ref:`MilestoneReference` для метрики.
