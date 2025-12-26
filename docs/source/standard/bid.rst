

.. index:: Bid, Parameter, LotValue, bidder, participant, pretendent

.. _bid:

Bid
===

Схема
-----

:tenderers:
    Список об’єктів :ref:`Tenderer`

:date:
    рядок, :ref:`date`, генерується автоматично

:id:
    uid, генерується автоматично

:status:
    рядок

    Можливі значення:

    * `draft`
    * `active`

    Можливі значення у :ref:`defense` and :ref:`openua`:

    * `draft`
    * `active`
    * `invalid`
    * `deleted`

    Можливі значення у :ref:`openeu` and :ref:`esco`:

    * `draft`
    * `pending`
    * `active`
    * `invalid`
    * `invalid.pre-qualification`
    * `deleted`

    Можливі значення у :ref:`competitivedialogue`:

    * `draft`
    * `pending`
    * `active`
    * `invalid`
    * `deleted`

:value:
    :ref:`Value`, обов’язково

    Правила валідації:

    * Значення `amount` повинно бути меншим за `Tender.value.amount`
    * Значення `currency` повинно бути або відсутнім, або співпадати з `Tender.value.currency`
    * Значення `valueAddedTaxIncluded` повинно бути або відсутнім, або співпадати з `Tender.value.valueAddedTaxIncluded`

:documents:
    Список об’єктів :ref:`Document`

    Відмінності у :ref:`competitivedialogue`, :ref:`cfaua`, :ref:`openeu`, :ref:`openua`, :ref:`defense` and :ref:`esco`:

        Список об’єктів :ref:`ConfidentialDocument`. Див. :ref:`confidential-documents`

:parameters:
    Список об’єктів :ref:`Parameter`

:lotValues:
    Список об’єктів :ref:`LotValue`

:participationUrl:
    URL-адреса

    Веб-адреса для участі в аукціоні.

:submissionDate:
    рядок, :ref:`date`

    Генерується автоматично, лише для читання.

    Дата підтвердження пропозиції

:items:
    Список об’єктів :ref:`BidItem`


Додатково у :ref:`defense`, :ref:`openua`, :ref:`openeu`, :ref:`esco` та :ref:`competitivedialogue`:

    :selfEligible':
        рядок, обов’язковий

        Підтверджує відповідність критеріям прийнятності, встановлених замовником в тендерній документації.

    :selfQualified:
        рядок, обов’язковий

        Підтверджує відсутність підстав для відмови від участі відповідно до статті 17 Закону України ”Про державні закупівлі”.

    :subcontractingDetails:
        рядок

        При поданні пропозиції учасник може додати інформацію про субпідрядника, заповнивши текстове поле довільної довжини.


Є декілька конвертів- контейнерів з документами, що регулюють час відкриття даних у :ref:`openeu` та :ref:`esco`:

    :financialDocuments:
        Список об’єктів :ref:`ConfidentialDocument`. Цей конверт може містити фінансову частину пропозиції (`commercialProposal` та `billOfQuantity`). Розкривається на посткваліфікації.

    :eligibilityDocuments:
        Список об’єктів :ref:`ConfidentialDocument`. Цей конверт повинен містити тільки технічну частину пропозиції (`technicalSpecifications` та `qualificationDocuments`). Розкривається на прекваліфікації.

    :qualificationDocuments:
        Список об’єктів :ref:`ConfidentialDocument`. Розкривається на посткваліфікації.

    :requirementResponses:
        Список об’єктів :ref:`RequirementResponse`

.. _Parameter:

Parameter
=========

Схема
-----

:code:
    рядок, обов’язковий

    Код критерію.

:value:
    float, обов’язково

    Значення критерію.

.. _LotValue:

LotValue
========

Схема
-----

:value:
    :ref:`Value`, обов’язково

    Правила валідації:

    * `amount` повинно бути меншим, ніж `Lot.value.amount`
    * `currency` повинно або бути відсутнім, або відповідати `Lot.value.currency`
    * `valueAddedTaxIncluded` повинно або бути відсутнім, або відповідати `Lot.value.valueAddedTaxIncluded`

:relatedLot:
    рядок

    ID пов’язаного :ref:`lot`.

:date:
    рядок, :ref:`date`, генерується автоматично


:participationUrl:
    URL-адреса

    Веб-адреса для участі в аукціоні.


Додатково у :ref:`defense`, :ref:`openua`, :ref:`openeu` та :ref:`competitivedialogue`:

:subcontractingDetails:
    рядок

    При поданні пропозиції учасник може додати інформацію про субпідрядника, заповнивши текстове поле довільної довжини.



Workflow in :ref:`openeu`, :ref:`esco` and :ref:`competitivedialogue`
---------------------------------------------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
        E [ label="deleted"]
        F [ label="invalid"]
         A -> B [dir="both"];
         A -> C;
         A -> D [dir="both"];
         A -> E;
         A -> F [dir="both"];
         B -> C;
         D -> C;
         E -> C;
         F -> C;
         F -> E;
    }

\* позначає початковий статус
