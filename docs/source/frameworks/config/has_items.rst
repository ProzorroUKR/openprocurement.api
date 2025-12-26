.. _frameworks_has_items:

hasItems
========

Поле `hasItems` - це булеве поле, яке визначає, чи повинен відбір мати номенклатуру.

Можливі значення для поля `hasItems` залежать від поля `frameworkType`:

.. csv-table::
   :file: csv/has-items-values.csv
   :header-rows: 1

hasItems має значення `false`
-----------------------------

`hasItems:false` означає, що номенклатура не дозволена для відбору.

Створімо відбір зі значенням `hasItems:false` з номенклатурою:

.. http:example:: http/has-items-false-with-items-create-error.http
   :code:

Бачимо помилку, яка вказує, що номенклатура не дозволена для відбору зі значенням `hasItems:false`.

Тепер створімо відбір зі значенням `hasItems:false` без номенклатури:

.. http:example:: http/has-items-false-without-items-create.http
   :code:

А потім активуємо її:

.. http:example:: http/has-items-false-without-items-activate-success.http
   :code:

Бачимо, що відбір успішно створений без номенклатури:

hasItems має значення `true`
----------------------------

`hasItems:true` означає, що номенклатура обов'язкова для відбору.

Створімо відбір зі значенням `hasItems:true` без номенклатури:

.. http:example:: http/has-items-true-without-items-create.http
   :code:

А потім активуємо її:

.. http:example:: http/has-items-true-without-items-activate-error.http
   :code:

Бачимо помилку, яка вказує, що номенклатура обов'язкова для відбору зі значенням `hasItems:true`.

Тепер створімо відбір зі значенням `hasItems:true` з номенклатурою:

.. http:example:: http/has-items-true-with-items-create.http
   :code:

А потім активуємо її:

.. http:example:: http/has-items-true-with-items-activate-success.http
   :code:

Бачимо, що відбір успішно створений з номенклатурою:

Пізніше, коли буде створено угоду, номенклатуру буде перенесено до угоди:

.. http:example:: http/has-items-true-with-items-agreement.http
   :code:
