
.. include:: defs.hrst

.. index:: Item, Parameter, Classification, CPV, Unit

.. _Item:

Item
====

Схема
-----

:id:
    рядок, генерується автоматично

:description:
    рядок, багатомовний, обов’язковий

    |ocdsDescription| Опис товарів та послуг, які повинні бути надані.

:classification:
    :ref:`Classification`

    |ocdsDescription| Початкова класифікація елемента. Дивіться у itemClassificationScheme, щоб визначити бажані списки класифікації, включно з CPV та GSIN.

    Класифікація `classification.scheme` обов’язково повинна бути `CPV` або `ДК021`. `classification.id` повинно бути дійсним CPV або ДК021 кодом.

:additionalClassifications:
    Список об’єктів :ref:`Classification`

    |ocdsDescription| Масив додаткових класифікацій для елемента. Дивіться у список кодів itemClassificationScheme, щоб використати поширені варіанти в OCDS. Також можна використовувати для представлення кодів з внутрішньої схеми класифікації.

    Об’єкт, у якого classification.id починаєтсья з 336, може мати не більше одного додаткового класифікатора зі scheme=INN.

    Об’єкт з classification.id=33600000-6 повинен обов’язково мати один додатковий класифікатор зі scheme=INN.

    Обов’язково мати хоча б один елемент з `ДКПП` у стрічці `scheme`.

    Validation depends on:

        * :ref:`NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM` constant
        * :ref:`CPV_336_INN_FROM` constant (for :ref:`Tender` :ref:`Item`)

:unit:
    :ref:`Unit`

    |ocdsDescription| Опис одиниці виміру товару, наприклад, години, кілограми. Складається з назви одиниці та значення однієї одиниці.

:quantity:
    ціле число

    |ocdsDescription| Кількість необхідних одиниць.

    Відсутня в :ref:`esco`

:deliveryDate:
    :ref:`Period`

    Період, протягом якого елемент повинен бути доставлений.

    Відсутня в :ref:`esco`

:deliveryAddress:
    :ref:`Address`

    Адреса місця, куди елемент повинен бути доставлений.

:deliveryLocation:
    словник

    Географічні координати місця доставки. Складається з таких компонентів:

    :latitude:
        рядок, обов’язковий
    :longitude:
        рядок, обов’язковий
    :elevation:
        рядок, не обов’язково, переважно не використовується

    `deliveryLocation` зазвичай має вищий пріоритет ніж `deliveryAddress`, якщо вони обидва вказані.

:relatedLot:
    рядок

    ID пов’язаного :ref:`lot`.

Додатково у :ref:`pricequotation`:

:profile:
    рядок, обов’язковий

    ID пов’язаного профілю


Додатково у :ref:`base-contracting`:

:attributes:
    Список з :ref:`ItemAttribute`


.. _BidItem:

BidItem
=======

Схема
-----

:id:
    рядок, генерується автоматично

:description:
    рядок, багатомовний, обов’язковий

    |ocdsDescription| Опис товарів та послуг, які повинні бути надані.

:unit:
    :ref:`Unit`

    |ocdsDescription| Опис одиниці виміру товару, наприклад, години, кілограми. Складається з назви одиниці та значення однієї одиниці.

:quantity:
    ціле число

    |ocdsDescription| Кількість необхідних одиниць.

:relatedLot:
    рядок

    ID пов’язаного :ref:`lot`.

Additionally in :ref:`belowthreshold` :ref:`openua`, :ref:`openeu`, :ref:`open`, :ref:`competitiveordering`, :ref:`esco` and :ref:`competitivedialogue`: :ref:`pricequotation`:

:product:
    рядок, обов’язковий

    ID пов’язаного продукту з маркету


.. _Classification:

Classification
==============

Схема
-----

:scheme:
    рядок

    |ocdsDescription| Класифікація повинна бути взята з існуючої схеми або списку кодів. Це поле використовується, щоб вказати схему/список кодів, з яких буде братись класифікація. Для класифікацій лінійних елементів це значення повинно представляти відому Схему Класифікації Елементів, де це можливо.

:id:
    рядок

    |ocdsDescription| Код класифікації взятий з вибраної схеми.

:description:
    рядок

    |ocdsDescription| Текстовий опис або назва коду.

:uri:
    uri

    |ocdsDescription| URI для ідентифікації коду. Якщо індивідуальні URI не доступні для елементів у схемі ідентифікації це значення треба залишити пустим.

    Регулярний вираз для цього поля: ``^https?://\S+$``

.. _Unit:

Unit
====

Схема
-----

:code:
    рядок, обов’язковий

    Код одиниці в UN/CEFACT Recommendation 20.

:name:
    рядок

    |ocdsDescription| Назва одиниці

Додатково у :ref:`limited`:

:value:
    :ref:`Value`

    Ціна за одиницю.
