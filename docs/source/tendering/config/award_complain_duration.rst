.. _award_complain_duration:

awardComplainDuration
=====================

Поле `awardComplainDuration` є цілим полем, що вказує тривалість оскарження результатів визначення виграшу

Можливі значення для поля `awardComplainDuration` залежать від поля `procurementMethodType`

.. csv-table::
   :file: csv/award-complain-duration-values.csv
   :header-rows: 1

awardComplainDuration is `true`
-------------------------------

Давайте створимо тендер `belowThreshold`:

.. http:example:: http/award-complain-duration-tender-post-1.http
   :code:

Потім додайте relevantLot для елемента:

.. http:example:: http/award-complain-duration-tender-patch-1.http
   :code:

Тут ми можемо перевірити, що поле "complaintPeriod" відсутнє у відповіді.
