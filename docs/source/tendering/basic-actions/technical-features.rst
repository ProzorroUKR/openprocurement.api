.. _technical_features:


Технічні характеристики
=======================


Процедури з технічними характеристиками
---------------------------------------

Процедури які підтримують технічні характеристики:
 - aboveThresholdUA
 - aboveThresholdEU
 - belowThreshold
 - competitiveDialogueUA
 - competitiveDialogueEU
 - competitiveDialogueUA.stage2
 - competitiveDialogueEU.stage2
 - competitiveOrdering
 - closeFrameworkAgreementUA
 - esco
 - priceQuotation


Створення закупівлі з технічними характеристами
-----------------------------------------------

Ви можете встановити індетифікатор обʼєкту з сервісу каталогів у поля `profile` чи `category` до передмету закупівлі.

Якщо вказанаий профіль чи категорія не існує в сервісі каталогів, ви отримаєте помилку:

.. http:example:: http/techfeatures/item-profile-not-found.http
   :code:


Також обʼєкт з каталогів повинен статус `active`:

.. http:example:: http/techfeatures/item-profile-not-active.http
   :code:

.. note::

    Для :ref:`pricequotation` поле `profile` обов'язкове, якщо:

        * відбір з каталогу

        * tender.value.amount >= 500000 UAH

        * tender.procuringEntity.kind != special/defense/other


Тож якщо ви встановите індертифікатор корректного профілю/категорію, ви зможете створити закупівлю:

.. http:example:: http/techfeatures/tender-with-item-profile-created.http
   :code:


Створення критерія технічних характеристик
------------------------------------------

Якщо ви хочете створити критерій технічних характеристик, потрібно встановити `CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES` у `criterion.classification.id` та `relatedItem` до предмету з повʼязаним профілем/категорією.

Якщо ви спробуєте створити критерій без `relatesTo`: `item` ви отримаєте помилку:

.. http:example:: http/techfeatures/create-tech-criteria-without-related-item.http
   :code:


Також якщо ви спробуєте створити критерій без `relatedItem` до предмету без полей `profile`/`category`, ви отримаєте помилку:

.. http:example:: http/techfeatures/create-tech-criteria-for-items-without-profile.http
   :code:


Тож якщо всі правила дотримані ви можете створити критерій технічних характеристик:

.. http:example:: http/techfeatures/tender-with-item-profile-created.http
   :code: