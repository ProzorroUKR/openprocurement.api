.. _qualification_complain_duration:

qualificationComplainDuration
=============================

Поле `qualificationComplainDuration` є цифровим полем, що визначає тривалість оскарження результатів кваліфікації.

Можливі значення для поля `qualificationComplainDuration` залежать від `procurementMethodType`

.. csv-table::
   :file: csv/qualification-complain-duration-values.csv
   :header-rows: 1

Examples
--------

Створемо тендер з `qualificationComplainDuration`, що дорівнює пʼяти дням:

.. http:example:: http/qualification-complain-duration-5-days.http
   :code:

Тендев успішно створено з очікуваними періодами подачі скарг, кожен з яких закінчується через пʼять днів після створення кваліфікації.
