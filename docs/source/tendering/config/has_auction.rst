.. _has_auction:

hasAuction
==========

Поле `hasAuction` є булевим полем, яке вказує, чи є аукціон у тендері чи ні. Тендер ніколи не перейде у статус `active.auction`, якщо `hasAuction` дорівнює `false`.

Можливі значення для поля `hasAuction` залежать від поля `procurementMethodType`.

.. csv-table::
   :file: csv/has-auction-values.csv
   :header-rows: 1

hasAuction встановлено у `true`
-------------------------------

Створимо тендер з `hasAuction` встановленим у `true`

.. http:example:: http/has-auction-true-tender-post.http
   :code:

І додамо лот до нього:

.. http:example:: http/has-auction-true-tender-add-lot.http
   :code:

Поле `minimalStep` обов'язкове для закупівель з аукціоном.

* Якщо закупівля безлотова, тоді це поле обов'язкове на рівні тендеру під час активації.

* Якщо закупівля лотова - тоді це поле обов'язкове на рівні лотів, але в закупівлі це поле заборонено вказувати і автоматично не записується як мінімальне значення з усіх лотів.

Якщо під час активації закупівля має лоти і на рівні закупівлі вказано `minimalStep`, тоді ми побачимо помилку, що це поле зайве в тендері:

.. http:example:: http/has-auction-true-tender-with-lots-minimal-step-rogue.http
   :code:

Подивимося на завершений тендер:

.. http:example:: http/has-auction-false-tender-complete.http
   :code:

hasAuction встановлено у `false`
--------------------------------

Тепер створимо тендер з `hasAuction` встановленим у `false`

.. http:example:: http/has-auction-false-tender-post.http
   :code:

Ви можете побачити, що в запиті відсутнє поле `minimalStep`, оскільки тендер без аукціону не має поля `minimalStep`.

І додамо лот до нього:

.. http:example:: http/has-auction-false-tender-add-lot.http
   :code:

Також відсутнє поле `minimalStep` в запиті.

Подивимося на завершений тендер:

.. http:example:: http/has-auction-false-tender-complete.http
   :code:

Різниця
-------

Подивимося на різницю завершених тендерів:

.. literalinclude:: json/has-auction-false-tender-complete.json
   :diff: json/has-auction-true-tender-complete.json

Різниця для тендеру з `hasAuction` встановленим у `false` порівняно з `true` є:

* немає поля `submissionMethod`

* немає поля `minimalStep`

* немає поля `auctionPeriod`

* немає поля `auctionUrl`

* немає поля `participationUrl`
