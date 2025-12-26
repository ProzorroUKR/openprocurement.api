.. _has_pre_selection_agreement:

hasPreSelectionAgreement
========================

Поле `hasPreSelectionAgreement` є булевим полем, яке вказує, чи закупівля має процедуру попереднього відбору та має бути зв'язана з угодою.

Можливі значення для поля `hasPreSelectionAgreement` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/has-pre-selection-agreement-values.csv
   :header-rows: 1

hasPreSelectionAgreement встановлено у `true`
---------------------------------------------

Якщо `hasPreSelectionAgreement` встановлено у `true`, то закупівля буде зв'язана з угодою. Це означає, що закупівля буде створена з полем `agreements`, яке має поле `id` всередині:

.. http:example:: http/has-pre-selection-agreement-true-tender-post.http
   :code:

Система перевіряє, чи дозволено закупівлю з вказаним `procurementMethodType` пов'язувати з угодою з певним `agreementType`. Поглянемо на діаграму дозволених зв'язків між `procurementMethodType` та `agreementType`:

.. image:: diagrams/tender_agreement_relations.png
   :alt: Tender Agreement Relations
   :width: 100%
   :align: center


При спробі створити закупівлю з вказаним `procurementMethodType`що не може бути пов'язано з угодою з вказаним `agreementType`, система поверне помилку:

.. http:example:: http/has-pre-selection-agreement-true-tender-post-invalid-type.http
   :code:

Стандартні правила
^^^^^^^^^^^^^^^^^^

Для закупівлі, яка пов'язана з угодою, застосовуються наступні перевірки під час створення:

* Якщо угода має номенклатуру, то номенклатура закупівлі повинна бути підмножиною номенклатури угоди

Для закупівлі, яка пов'язана з угодою, застосовуються наступні перевірки під час активації:

* угода повинна бути активна


dynamicPurchasingSystem -> competitiveOrdering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Для закупівлі, яка пов'язана з угодою, застосовуються наступні перевірки під час створення:

* угода не повинна мати номенклатур
* ідентифікатор та схема ідентифікатора постачальника повинні співпадати в угоді та закупівлі

Для закупівлі, яка пов'язана з угодою, застосовуються наступні перевірки під час активації:

* угода повинна мати принаймні 3 активні контракти

:ref:`competitiveordering` → :ref:`competitiveordering_short_tutorial`

electronicCatalogue -> priceQuotation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Для закупівлі, яка пов'язана з угодою, застосовуються наступні перевірки під час активації:

* угода повинна мати принаймні 1 активний контракт
* профіль кожної номенклатури повинен належати тій же угоді, що і закупівля

:ref:`pricequotation` → :ref:`pricequotation_tutorial`

internationalFinancialInstitutions -> requestForProposal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Для закупівлі, яка пов'язана з угодою, застосовуються наступні перевірки під час активації:

* угода повинна мати принаймні 3 активні контракти
* ідентифікатор та схема ідентифікатора постачальника повинні співпадати в угоді та закупівлі

:ref:`requestforproposal` → :ref:`requestforproposal_tutorial`


Особливі правила
^^^^^^^^^^^^^^^^

Деякі процедури мають особливості у правилах зв'язку з угодою.


closeFrameworkAgreementUA -> closeFrameworkAgreementSelectionUA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:ref:`cfaselectionua` → :ref:`cfaselection_tutorial`
