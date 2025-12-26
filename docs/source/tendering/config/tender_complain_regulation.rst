.. _tender_complain_regulation:

tenderComplainRegulation
========================

Поле `tenderComplainRegulation` – цілочисельне поле, яке визначає кінцеву дату періоду оскарження умов тендерної документації відповідно до кінцевого терміну подання тендерних пропозицій.

Можливі значення поля `tenderComplainRegulation` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/tender-complain-regulation-values.csv
   :header-rows: 1

Особливості конфігурації
------------------------

Давайте створимо тендер `belowThreshold`:

.. http:example:: http/tender-complain-regulation-tender-post-2.http
   :code:

Потім додайте relatedLot для елемента:

.. http:example:: http/tender-complain-regulation-tender-patch-2.http
   :code:

Тут ми можемо перевірити, що поле "complaintPeriod" відсутнє у відповіді.

Тепер давайте створимо тендер `aboveThreshold`:

.. http:example:: http/tender-complain-regulation-tender-post-1.http
   :code:

Потім додайте relatedLot для елемента:

.. http:example:: http/tender-complain-regulation-tender-patch-1.http
   :code:

Ми побачимо, що відповідь містить поле "complaintPeriod", що означає, що період подання скарги відображатиметься для тендерів із значенням `tenderComplainRegulation`, вищим за 0