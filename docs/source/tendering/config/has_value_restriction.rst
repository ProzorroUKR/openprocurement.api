.. _has_value_restriction:

hasValueRestriction
===================

Поле `hasValueRestriction` є булевим полем, яке вказує, що ціна тендерної пропозиції може перевищувати очікувану вартість предмета закупівлі, зазначену в оголошенні про проведення.

Можливі значення для поля `hasValueRestriction` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/has-value-restriction-values.csv
   :header-rows: 1

hasValueRestriction встановлено у `true`
----------------------------------------

`hasValueRestriction:true` означає, що ціна тендерної пропозиції не може перевищувати очікувану вартість предмета закупівлі.

Створимо тендер з лотами з `hasValueRestriction` встановленим у `true`:

.. http:example:: http/has-value-restriction-true-tender-lots-post.http
   :code:

І додамо пропозицію до тендера з вартістю більшою за очікувану вартість, оголошену у лоті:

.. http:example:: http/has-value-restriction-true-tender-lots-add-invalid-bid.http
   :code:

В цьому випадку ми побачимо помилку, що додавання пропозиції з вартістю більшою за очікувану вартість заборонено.

Додамо пропозицію до тендера з вартістю меншою за очікувану вартість, оголошену у лоті:

.. http:example:: http/has-value-restriction-true-tender-lots-add-valid-bid.http
   :code:

Спробуємо відредагувати вартість пропозиції на більшу за очікувану вартість, оголошену у лоті, і ми побачимо помилку, тому що це заборонено конфігурацією `hasValueRestriction:true`.

.. http:example:: http/has-value-restriction-true-tender-lots-patch-bid.http
   :code:


hasValueRestriction встановлено у `false`
-----------------------------------------

`hasValueRestriction:false` означає, що ціна тендерної пропозиції може перевищувати очікувану вартість предмета закупівлі.


Створимо тендер з лотами з `hasValueRestriction` встановленим у `false`:

.. http:example:: http/has-value-restriction-false-tender-lots-post.http
   :code:

І додамо пропозицію до тендера з вартістю більшою за очікувану вартість, оголошену у лоті:

.. http:example:: http/has-value-restriction-false-tender-lots-add-valid-bid.http
   :code:

В цьому випадку ми не побачимо ніякої помилки, тому що додавання пропозиції з вартістю більшою за очікувану вартість дозволено конфігурацією `hasValueRestriction:false`.
