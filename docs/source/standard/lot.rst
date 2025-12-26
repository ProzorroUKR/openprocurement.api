.. include:: defs.hrst

.. index:: Lot

.. _Lot:

Lot
===

Схема
-----

:id:
    рядок, генерується автоматично

:title:
   рядок, багатомовний

   Назва лота закупівлі.

:description:
   рядок, багатомовний

   Детальний опис лота закупівлі.

:value:
   :ref:`value`, обов’язково

   Повний доступний бюджет лота закупівлі. Цінові пропозиції, більші ніж ``value``, будуть відхилені.

   Відсутнє в :ref:`esco`

:guarantee:
    :ref:`BasicValue`

    Забезпечення тендерної пропозиції

    Відсутнє в :ref:`limited`
                         
:date:
    рядок, :ref:`date`, генерується автоматично
                                           
:minimalStep:
   :ref:`value`, обов’язково

   Мінімальний крок аукціону (редукціону). Правила валідації:

   * `amount` повинно бути меншим, ніж `Lot.value.amount`
   * `currency` повинно або бути відсутнім, або відповідати `Lot.value.currency`
   * `valueAddedTaxIncluded` повинно або бути відсутнім, або відповідати `Lot.value.valueAddedTaxIncluded`

   Робочий процес у :ref:`limited` and :ref:`esco`

:auctionPeriod:
   :ref:`period`, доступно лише для читання

   Період проведення аукціону.

   Відсутнє в :ref:`limited`

:auctionUrl:
    URL-адреса

    Веб-адреса для перегляду аукціону.

    Відсутнє в :ref:`limited`

:status:
   рядок

   :`active`:
       Активний лот закупівлі (активний)
   :`unsuccessful`:
       Неуспішний лот закупівлі (не відбувся)
   :`complete`:
       Завершено лот закупівлі (завершено)
   :`cancelled`:
       Скасовано лот закупівлі (скасовано)

   Статус лота.

Додатково у :ref:`esco`:

:minimalStepPercentage:
   float, обов’язково

  Minimum step increment of the energy service contract performance indicator during auction that is calculated on participant’s bid. Possible values: from 0.005 to 0.03 (from 0.5% to 3% respectively) with 3-digit precision after comma.

:fundingKind:
    рядок, обов’язковий

:Lot funding source:

    Можливі значення:

    * budget -  Budget funding.
    * other - Supplier funding.

    Default value: other

:yearlyPaymentsPercentageRange:
    float, обов’язково

    Fixed percentage of participant's cost reduction sum, with 3-digit precision after comma.

    Можливі значення:

   * from 0.8 to 1 (from 80% to 100% respectively) if lot:fundingKind:other.
   * from 0 to 0.8 (from 0% to 80% respectively) if lot:fundingKind:budget.

     Input precision - 3 digits after comma.


Робочий процес у :ref:`limited`, :ref:`esco` та :ref:`openeu`
-------------------------------------------------------------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="complete"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
         A -> B;
         A -> C;
         A -> D;
    }

\* позначає початковий стан