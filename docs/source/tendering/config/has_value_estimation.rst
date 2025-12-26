.. _has_value_estimation:

hasValueEstimation
==================

Поле `hasValueEstimation` є булевим полем, яке вказує на наявність або відсутнісь у закупівлі очікуваної вартості.

Можливі значення для поля `hasValueEstimation` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/has-value-estimation-values.csv
   :header-rows: 1

hasValueEstimation встановлено у `true`
---------------------------------------

`hasValueEstimation:true` означає, що закупівля має очікувану вартість.

Створимо тендер з `hasValueEstimation` встановленим в `true`

.. http:example:: http/has-value-estimation-true-tender-lots-post.http
   :code:

Тендер з очікуваною вартістю успішно створено.

І додамо в нього лоти:

.. http:example:: http/has-value-estimation-true-tender-lots-add-post.http
   :code:

Лот з очікуваною вартістю успішно додано.

Подивимося на тендер:

.. http:example:: http/has-value-estimation-true-tender-lots-add-post.http
   :code:

hasValueEstimation встановлено у `false`
----------------------------------------

`hasValueEstimation:false` означає, що закупівля не має очікуваної вартості. Система буде відхиляти очікувану вартість тендера, якщо вона буде передана.

Створимо тендер з `hasValueEstimation` встановленим в `false` і вказаною очікуваною вартістю:

.. http:example:: http/has-value-estimation-false-tender-lots-post-invalid.http
   :code:

В цьому випадку ми побачимо помилку, що створення тендеру з очікуваною вартістю заборонено.

Створимо тендер з `hasValueEstimation` встановленим в `false` без очікуваної вартості:

.. http:example:: http/has-value-estimation-false-tender-lots-post.http
   :code:

Таке ж правило для лотів. Система буде відхиляти очікувану вартість лота, якщо вона буде вказана.

Додамо лот з очікуваною вартістю:

.. http:example:: http/has-value-estimation-false-tender-lots-add-post-invalid.http
   :code:

В цьому випадку ми побачимо помилку, що створення лоту з очікуваною вартістю заборонено.

Додамо лот без очікуваної вартості:

.. http:example:: http/has-value-estimation-false-tender-lots-add-post.http
   :code:

Подивимося на тендер:

.. http:example:: http/has-value-estimation-false-tender-complete.http
   :code:

Різниця
-------

Різниця для тендерів з `hasValueEstimation` встановленим у `false` порівняно з `true` є

* тендери не мають поля ``value:amount``, передавати його заборонено

* лоти не мають поля ``value:amount``, передавати його заборонено
