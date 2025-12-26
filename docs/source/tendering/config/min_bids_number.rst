.. _min_bids_number:

minBidsNumber
=============

Поле `minBidsNumber` є ціло-числовим полем, яке встановлює достатню кількість пропозицій для того, щоб процедура відбулась.

Можливі значення для поля `minBidsNumber` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/min-bids-number-values.csv
   :header-rows: 1

Особливості конфігурації
------------------------

* Значення поля має бути в діапазоні від 1 до 9

Створимо тендер `belowThreshold` з конфігурацією `minBidsNumber=0` і побачимо помилку:

.. http:example:: http/min-bids-number-invalid-value-1.http
   :code:

Створимо тендер `belowThreshold` з конфігурацією `minBidsNumber=10` і побачимо помилку:

.. http:example:: http/min-bids-number-invalid-value-2.http
   :code:

* Значення вказується на рівні тендеру. Якщо процедура містить >1 lots, то це значення застосовується однаково до кожного лоту:

.. note::
    Вказуємо `minBidsNumber` на рівні тендеру `minBidsNumber=2` тоді `lot1=2; lot2=2; lotX=2`

* Якщо по закінченню періоду прийому пропозицій подано менше пропозицій, ніж вказано в полі `minBidsNumber`, то процедура автоматично переходить до статусу `unsuccessful`, а на майданчику та на офіційному порталі закупівля відображається, як `Торги не відбулися`.

Створимо тендер `belowThreshold` з конфігурацією `minBidsNumber=2` і одним бідом:

.. http:example:: http/min-bids-number-tender-post-1.http
   :code:

Подивимося на тендер після закінчення `active.tendering` періоду:

.. http:example:: http/min-bids-number-tender-unsuccessful.http
   :code:

* Якщо встановлено значення `hasAuction:true`, `minBidsNumber=1` та після завершення періоду прийому пропозицій подано `bids=1`, то система автоматично реєструє учасника як потенційного переможця, закупівля переводиться до статусу «Кваліфікація» `active.qualification`.

Створимо тендер `belowThreshold` з конфігурацією `minBidsNumber=1` і одним бідом:

.. http:example:: http/min-bids-number-tender-post-2.http
   :code:

Подивимося на тендер після закінчення `active.tendering` періоду, аукціон буде пропущений і одразу розпочнеться `active.qualification` період:

.. http:example:: http/min-bids-number-tender-qualification-1.http
   :code:

* Якщо встановлено значення `hasAuction:true`, пропозицій подано >=2 та кількість пропозицій проходить перевірку по полю minBidsNumber, то система активує єдиний модуль «Аукціон».

Створимо тендер `belowThreshold` з конфігурацією `minBidsNumber=2` і двома бідами:

.. http:example:: http/min-bids-number-tender-post-3.http
   :code:

Подивимося на тендер після закінчення `active.tendering` періоду, розпочнеться аукціон:

.. http:example:: http/min-bids-number-tender-auction.http
   :code:

Після закінчення `active.auction`, система повинна запустити `active.qualification`. Дивимось знову на значення `minBidsNumber:2` та перевіряємо наявність активних bids. Їх два? Так, запускаємо `active.qualification`:

.. http:example:: http/min-bids-number-tender-qualification-2.http
   :code:
