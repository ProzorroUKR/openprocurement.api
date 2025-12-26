.. index:: Milestone

.. _milestone:

Milestone
=========

Схема
-----

:id:
    uid, генерується автоматично

:title:
    рядок, обов’язковий

    Значення заповнюються згідно з `milestones <https://prozorroukr.github.io/standards/codelists/milestones/title.json>`__ довідниками.

:description:
    рядок, обов’язковий якщо title == `anotherEvent`

:type:
    рядок, обов’язковий

    Єдине можливе значення:

    * `financing`
    * `delivery`

:code:
    рядок, обов’язковий

    Значення заповнюються згідно з `milestones <https://prozorroukr.github.io/standards/codelists/milestones/code.json>`_ довідниками.

:percentage:
    float, 0..100

    Сума всіх milestone тендеру (або лоту) повинна бути 100

:duration:
    :ref:`Duration`, обов’язково

:sequenceNumber:
    integer, обов’язковий, не негативний

:relatedLot:
    uid

    ID пов’язаного :ref:`lot`.


Milestone в :ref:`frameworks_electroniccatalogue`
=================================================

Схема
-----

:id:
    uid, генерується автоматично

:type:
    рядок, обов’язковий

    Єдине можливе значення:

    * `activation`
    * `ban`

:status:
    string

    Єдине можливе значення:

    * `scheduled`
    * `met`
    * `notMet`
    * `partiallyMet`

:dueDate:
    рядок, :ref:`date`

:documents:
    Список об'єктів :ref:`document`

:dateModified:
    рядок, :ref:`date`, генерується автоматично, лише для читання

    Дата зміни майлстону

:dateMet:
    рядок, :ref:`date`


.. _ContractMilestone:

ContractMilestone
=================

Схема
-----

:id:
    uid, генерується автоматично

:title:
    рядок, обов’язковий

    Значення заповнюються згідно з `milestones <https://prozorroukr.github.io/standards/codelists/milestones/title.json>`__ довідниками.

:description:
    рядок, обов’язковий якщо title == `anotherEvent`

:type:
    рядок, обов’язковий

    Єдине можливе значення:

    * `financing`
    * `delivery`

:code:
    рядок, обов’язковий

    Значення заповнюються згідно з `milestones <https://prozorroukr.github.io/standards/codelists/milestones/code.json>`_ довідниками.

:percentage:
    float, 0..100

    Сума всіх milestone тендеру (або лоту) повинна бути 100

:duration:
    :ref:`Duration`, обов’язково

:sequenceNumber:
    integer, обов’язковий, не негативний

:relatedLot:
    uid

    ID пов’язаного :ref:`lot`.

:status:
    string

    Єдине можливе значення:

    * `scheduled`

:dateMet:
    рядок, :ref:`date`

.. _Duration:

Duration
========

Схема
-----

:days:
    integer, обов’язковий, не негативний

:type:
    рядок, обов’язковий

    Можливі значення:

    * `working`
    * `banking`
    * `calendar`
