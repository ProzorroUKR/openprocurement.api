.. _value_currency_equality:

valueCurrencyEquality
=====================

Поле `valueCurrencyEquality` є булевим полем, яке вимикає перевірку `currency of bid should be identical to currency of value of tender`. Це означає, що в процедурі застосовується мультивалютність.

Можливі значення для поля `valueCurrencyEquality` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/value-currency-equality-values.csv
   :header-rows: 1

valueCurrencyEquality встановлено у `true`
------------------------------------------

`valueCurrencyEquality:true` означає, що буде працювати валідація при поданні пропозиції і система перевірить чи валюта тендерної пропозиції ідентична валюті очікуваної вартості в тендері/лоті.

Створимо багатолотовий тендер з `valueCurrencyEquality` встановленим у `true`:

.. http:example:: http/value-currency-equality-true-tender-lots-post.http
   :code:

І додамо до нього пропозицію з іншою валютою, ніж вказано в очікуваній вартості лоту:

.. http:example:: http/value-currency-equality-true-tender-lots-add-invalid-bid.http
   :code:

В цьому випадку ми побачимо помилку, що додавання пропозиції в іншій валюті - заборонено.

Додамо пропозицію до тендера з валютою ідентичною з очікуваною вартістю тендера/лота:

.. http:example:: http/value-currency-equality-true-tender-lots-add-valid-bid.http
   :code:

Учасник подає пропозицію, де `bid:value:currency = tender:value:currency`, при спробі передати іншу валюту система видає помилку. Спробуємо змінити валюту пропозиції на іншу і побачимо помилку, що це забронено зі встановленою конфігурацією `valueCurrencyEquality:true`.

.. http:example:: http/value-currency-equality-true-tender-lots-patch-bid.http
   :code:

valueCurrencyEquality встановлено у `false`
-------------------------------------------

`valueCurrencyEquality:false` означає, що валідація стосовно валюти працювати не буде.

.. note::
    Мультивалютність може бути застосована лише при `hasAuction:false` та при `hasAwardingOrder:false` та при `hasValueRestriction:false`.

Створимо багатолотовивй тендер з `valueCurrencyEquality` встановленим у `false`:

.. http:example:: http/value-currency-equality-false-tender-lots-post.http
   :code:

І додамо до нього пропозицію з іншою валютою, ніж вказано в очікуваній вартості лоту:

.. http:example:: http/value-currency-equality-false-tender-lots-add-valid-bid.http
   :code:

В цьому випадку ми не побачимо ніяку помилку, тому що додавання пропозиції в іншій валюті - дозволено.

Замовник та учасник укладають договір у тій валюті, в якій було вказано пропозицію учасником. Подивимося на завершений тендер, валюта вартості в аварді і договорі така ж сама як і в пропозиції:

.. http:example:: http/value-currency-equality-false-tender-complete.http
   :code:
