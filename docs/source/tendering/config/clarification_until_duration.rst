.. _clarification_until_duration:

clarificationUntilDuration
==========================

Поле `clarificationUntilDuration` є цифровим полем, яке встановлює кількість днів для надання відповіді замовником на звернення.

Можливі значення для поля `clarificationUntilDuration` в залежності від поля `procurementMethodType`:

.. csv-table::
   :file: csv/clarification-until-duration-values.csv
   :header-rows: 1


Examples
--------

Cтворимо тендер з `clarificationUntilDuration`, що становить один робочий день:

.. http:example:: http/clarification-until-duration-1-working-day.http
   :code:

Тендер успішно створено з очікуваним значенням clarificationUntil, яке закінчується через один робочий день після створення enquiryPeriod startDate.

Створимо тендер з `clarificationUntilDuration`, що становить три календарні дні:

.. http:example:: http/clarification-until-duration-3-calendar-days.http
   :code:

Тендер успішно створено з очікуваним значенням clarificationUntil, яке закінчується через три календарні дні після створення enquiryPeriod startDate.

Створимо тендер з `clarificationUntilDuration`, що становить три робочих дні:

.. http:example:: http/clarification-until-duration-3-working-days.http
   :code:

Тендер успішно створено з очікуваним значенням clarificationUntil, яке закінчується через три робочих дні після створення enquiryPeriod startDate.
