.. _frameworks_clarification_until_duration:

clarificationUntilDuration
==========================

Поле `clarificationUntilDuration` -  це числове поле, яке встановлює кількість днів для надання відповіді замовником на звернення.

Можливі значення для `clarificationUntilDuration` в залежності від поля `frameworkType`:

.. csv-table::
   :file: csv/clarification-until-duration-values.csv
   :header-rows: 1


Examples
--------

`clarificationsUntil` розраховується під час створення рамочної угоди. Для типу `dynamicPurchasingSystem` це 3 робочих дні, як ви можете побачити нижче в `enquiryPeriod`:


.. http:example:: http/restricted/framework-with-agreement.http
   :code:

Як ви можете побачити, поле `clarificationsUntil` випереджає поле `endDate` на 3 робочих дні.