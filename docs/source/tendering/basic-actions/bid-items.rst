.. _bid_items:


Предмет закупівлі в пропозиції
==============================

Предмет закупівлі в пропозиції доступний у всіх типах процедур


Створюємо пропозицію з предметом закупівлі
------------------------------------------

Щоб створити пропозицію з предметом закупівлі, вам потрібно передати поле items зі значенням, що містить список :ref:`BidItem`.

Якщо ви спробуєте передати предмет закупівлі з id, якого не існує в tender.items, ви отримаєте помилку:

.. http:example:: http/bid-items-localization/unsuccessful-create-bid-with-items.http
   :code:

VAT для `items.unit.value` може мати лише значення `False`. Якщо ви спробуєте передати значення `True`, ви отримаєте помилку:

.. http:example:: http/bid-items-localization/unsuccessful-create-bid-with-items-VAT.http
   :code:

Надішлемо правильні дані:

.. http:example:: http/bid-items-localization/successfuly-create-bid-with-items.http
   :code:


Оновлення предмету закупівлі
----------------------------

Ви можете оновити `quantity` та `unit` предмета закупівлі в пропозиції

Щоб оновити дані в items, вам потрібно передати всі елементи зі списку разом з усіма даними; в іншому випадку, дані, які не передані, будуть втрачені:

.. http:example:: http/bid-items-localization/update-bid-items.http
   :code:


.. _bid_product_items:


Продукт в предметі закупівлі пропозиції
=======================================

Замість використання eligibleEvidence у критерії та evidence у відповідях, можна використовувати `product` у `bid.items`.

Процедури з продуктом в предметі закупівлі
------------------------------------------

Продукт в предмет закупівлі доступний у таких процедурах:
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


Стоврення пропозиції з продуктом в предметі закупівлі
-----------------------------------------------------

Все що вам потрібно це вказати ідентифікатор активного продукту з маркету в полі `product` у bid.items.


Якщо ви спробуєте передати не існуючий ідентифікатор, ви отримаєте помилку:

.. http:example:: http/bid-items-localization/item-product-not-found.http
   :code:


Якщо ви спробуєте передати ідентифікатор продукту зі статусом `hidden`, ви отримаєте помилку:

.. http:example:: http/bid-items-localization/item-product-not-active.http
   :code:

Якщо ви спробуєте передати ідентифікатор продукту з іншим знченням в полі `relatedCategory` аніж `category` в айтемі тендера, ви отримаєте помилку:

.. http:example:: http/bid-items-localization/item-product-invalid-related-category.http
   :code:


тже, якщо всі правила дотримані, ви можете створити пропозицію з продуктом у предметі закупівлі:

.. http:example:: http/bid-items-localization/bid-with-item-product-created.http
   :code:


Оновлення продукту в предметі закупівлі
---------------------------------------

Ви можете змінити ідентифікатор продукту, використовуючи метод `PATCH` для пропозиції (усі перевірки, що здійснюються під час створення, також застосовуються під час оновлення):

.. http:example:: http/bid-items-localization/update_bid-with-item-product.http
   :code: