.. _FrameworkChange:

FrameworkChange
===============

Схема
-----

:id:
    uid, генерується автоматично

:rationaleType:
    рядок, обов'язковий

    Тип причини  додання змін для відбору

    Можливі значення вказані в довіднику `framework period change causes <https://prozorroukr.github.io/standards/codelists/framework/framework_period_change_causes.json>`_.

:rationale:
    рядок, багатомовний, обов'язковий

    Причина для зміни відбору.

:modifications:
    Список об'єктів :ref:`FrameworkChangeModifications`

:previous:
    Список об'єктів :ref:`FrameworkChangeModifications` з попередніми значеннями відбору.

:date:
    рядок, :ref:`date`, генерується автоматично

    Дата внесення змін.

:dateModified:
    pядок, :ref:`date`, генерується автоматично

:documents:
    Список об’єктів :ref:`Document`


.. _FrameworkChangeModifications:

FrameworkChangeModifications
============================

Схема
-----

:qualificationPeriod:
   :ref:`period`, обов’язково

   Період, коли приймаються рішення щодо заявок постачальників. Повинна бути вказана хоча б `endDate` дата.
