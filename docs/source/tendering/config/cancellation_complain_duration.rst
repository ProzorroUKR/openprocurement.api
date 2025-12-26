.. _cancellation_complain_duration:

cancellationComplainDuration
============================

Поле `cancellationComplainDuration` - це ціле поле, яке вказує тривалість оскарження результатів визначення виграшу

Можливі значення поля `cancellationComplainDuration` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/cancellation-complain-duration-values.csv
   :header-rows: 1

cancellationComplainDuration is `true`
--------------------------------------

Давайте створимо тендер `belowThreshold`:

.. http:example:: http/cancellation-complain-duration-tender-post-2.http
   :code:

Потім додайте relevantLot для елемента:

.. http:example:: http/cancellation-complain-duration-tender-patch-2.http
   :code:

Тут ми можемо перевірити, що поле "complaintPeriod" відсутнє у відповіді.

Тепер давайте створимо тендер `aboveThreshold`:

.. http:example:: http/cancellation-complain-duration-tender-post-1.http
   :code:

Потім додайте relevantLot для елемента:

.. http:example:: http/cancellation-complain-duration-tender-patch-1.http
   :code:

Ми побачимо, що відповідь містить поле "complaintPeriod", що означає, що період скарги відображатиметься для тендерів із `cancellationComplainDuration` вищим за 0