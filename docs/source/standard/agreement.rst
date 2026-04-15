.. include:: defs.hrst

.. index:: Agreement
.. _agreement:

Agreement in :ref:`frameworks_electroniccatalogue`
==================================================

Схема
-----

:id:
    ID користувача, обов'язково, генерується автоматично

:agreementID:
    рядок, генерується автоматично, лише для читання

:agreementType:
    рядок, генерується автоматично, значення: `electronicCatalogue`, лише для читання

:frameworkID:
    рядок, генерується автоматично, лише для читання

:status:
    рядок, обов'язково

     Актуальний статус реєстру. Можливі значення:

    * `active`
    * `terminated`

:terminationDetails:
    рядок

:date:
    рядок, :ref:`date`, генерується автоматично, лише для читання

    Дата зміни реєстру

:dateModified:
    рядок, :ref:`date`, генерується автоматично, лише для читання

    Дата зміни реєстру.

:dateCreated:
    рядок, :ref:`date`, генерується автоматично, лише для читання

    Дата створення реєстру.

:procuringEntity:
   :ref:`ProcuringEntity`, генерується автоматично, лише для читання

   Organization conducting the agreement.

:period:
    :ref:`Period`

    Період чинності реєстру.

:classification:
   :ref:`Classification`, генерується автоматично, лише для читання

:additionalClassifications:
    список з :ref:`Classification`, генерується автоматично з угоди, лише для читання

:contracts:
    Список об'єктів :ref:`Contract`

:items:
    Список об'єктів :ref:`Item`

:frameworkDetails:
    рядок


.. _agreement_cfaua:

Agreement в :ref:`cfaua`
========================

Схема
-----

:id:
    ID користувача, обов'язково, генерується автоматично

:agreementID:
    рядок, генерується автоматично, лише для читання

:agreementNumber:
    рядок

:agreementType:
    string, value: `closeFrameworkAgreementUA`

:changes:
    Список  :ref:`ChangeTaxRate`, :ref:`ChangeItemPriceVariation`, :ref:`ChangePartyWithdrawal` або :ref:`ChangeThirdParty` об'єктів.

    Тільки в контейнері `agreements`.

:date:
    рядок, :ref:`date`, генерується автоматично, лише для читання
                                                             
    Дата зміни реєстру.

:dateModified:
    рядок, :ref:`date`, генерується автоматично, лише для читання

    Дата зміни реєстру.

:dateCreated:
    рядок, :ref:`date`, генерується автоматично, лише для читання

    Дата створення реєстру.

:dateSigned:
    рядок, :ref:`date`
                  
    Дата підписання угоди

:description:
    рядок, багатомовний
                   
    Опис договору

:description_en:
    рядок, багатомовний
                   
    Опис договору

:description_ru:
    рядок, багатомовний
                   
    Опис договору

:documents:
    Список об'єктів :ref:`Document`
                               
    |ocdsDescription| Всі документи і додатки, що стосуються угоди, в тому числі будь-які сповіщення.

:items:
    Список об'єктів :ref:`Item`

:features:
    Список об'єктів :ref:`Feature`

:milestones:
    Список об'єктів :ref:`milestone`

:period:
    :ref:`Period`
             
    Період чинності угоди. Щонайбільше 4 роки.

:status:
    рядок, обов'язково

     Актуальний статус реєстру. Можливі значення:

    * `pending` - угода в процесі підписання між замовником та :ref:`Contract`
    * `unsuccessful` - угода між замовником та :ref:`Contract` не було підписано
    * `active` - угода між замовником та :ref:`Contract` підписана
    * `cancelled` - підписання угоди скасовано через відміну закупівлі/лоту.

     Відмінності в контейнері `agreement`:

    * `active` - угода є активною і може бути використана для створення `selection` процедури
    * `terminated` - угода не може бути використана для створення `selection` процедури

:terminationDetails:
    рядок

:contracts:
    Список об'єктів :ref:`Contract`

:procuringEntity:
   :ref:`ProcuringEntity`, генерується автоматично, лише для читання

:numberOfContracts:
    ціле число, генерується автоматично, лише для читання

    Кількість активних контрактів в угоді.

:title:
    рядок

    Назва угоди

:title_ru:
    рядок

    Назва угоди

:title_en:
    рядок

    Назва угоди

Послідовність дій
-----------------

.. graphviz::

    digraph G {
        A [ label="pending" ]
        B [ label="active" ]
        C [ label="cancelled" ]
        D [ label="unsuccessful"]
         A -> B;
         A -> C;
         A -> D;
    }

Робочий процес у :ref:`agreementcfaua`
--------------------------------------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="terminated"]
         A -> B;
    }

\* позначає початковий статус

.. _agreement_pricequotation:

Agreement в :ref:`pricequotation`
=================================

Схема
-----

:id:
    uid, обов’язково

    ID пов’язаної угоди з :ref:`frameworks_electroniccatalogue`
