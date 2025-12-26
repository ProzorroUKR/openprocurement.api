
.. include:: defs.hrst

.. index:: Claim, dispute

.. _claim:

Claim
=====

Схема
-----

:id:
    uid, генерується автоматично

:author:
    :ref:`Organization`, обов’язково

    Організація, яка подає вимогу (contactPoint - людина, identification - організація, яку ця людина представляє).

:title:
    рядок, обов’язковий

    Заголовок вимоги.

:description:
    Опис запитання.

:date:
    рядок, :ref:`date`, генерується автоматично

    Дата подання.

:dateSubmitted:
    рядок, :ref:`date`, генерується автоматично

    Дата, коли вимога була подана.

:dateAnswered:
    рядок, :ref:`date`, генерується автоматично

    Дата, коли замовник відповів на вимогу.


:dateDecision:
    рядок, :ref:`date`, генерується автоматично

    День прийняття рішення по вимозі.

:dateCanceled:
    рядок, :ref:`date`, генерується автоматично

    Дата відхилення.

:status:
    рядок

    Можливі значення:

    * `draft` - чорновик, початковий етап
    * `claim` - вимога
    * `answered` - дано відповідь
    * `invalid` - недійсно
    * `declined` - відхилено
    * `resolved` - вирішено
    * `cancelled` - відхилено

:type:
    рядок

    Можливі значення типу:

    * `claim` - вимога

:resolution:
    рядок

    Рішення замовника.

:resolutionType:
    рядок

    Можливі значення типу вирішення:

    * `invalid` - недійсно
    * `declined` - відхилено
    * `resolved` - вирішено

:satisfied:
    bool

    Вимога задовільнена?

:decision:
    рядок

    Рішення органу оскарження.

:cancellationReason:
    рядок

    Причини відхилення.

:documents:
    Список об’єктів :ref:`ConfidentialDocument`

:relatedLot:
    рядок

    Ідентифікатор пов’язаного :ref:`lot`-а.

:tendererAction:
    рядок

    Дія учасника.

:tendererActionDate:
    рядок, :ref:`date`, генерується автоматично

    Дата дії учасника.


