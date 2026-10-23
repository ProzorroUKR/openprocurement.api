.. _opentendering_config:

Конфігурація відкритих торгів ``openTendering``
===============================================

Значення конфігурації визначаються різновидом закупівлі (``procurementMethodSubtype``). Замовник обирає
лише ``hasAuction`` та ``hasValueRestriction``; решта значень фіксовані для різновиду.

.. list-table::
   :header-rows: 1

   * - Config
     - UA
     - EU
   * - hasAuction
     - true / false (default true)
     - true / false (default true)
   * - hasAwardingOrder
     - true
     - true
   * - hasValueRestriction
     - true / false (default true)
     - true / false (default true)
   * - valueCurrencyEquality
     - true
     - true
   * - hasPrequalification
     - false
     - true
   * - minBidsNumber
     - 1
     - 1
   * - hasPreSelectionAgreement
     - false
     - false
   * - hasTenderComplaints / hasAwardComplaints / hasCancellationComplaints
     - true
     - true
   * - hasValueEstimation
     - true
     - true
   * - hasQualificationComplaints
     - false
     - true
   * - tenderComplainRegulation
     - 4 (календарні)
     - 4 (календарні)
   * - qualificationComplainDuration
     - 0
     - 10 (календарні)
   * - awardComplainDuration
     - 10 (календарні)
     - 10 (календарні)
   * - cancellationComplainDuration
     - 10 (календарні)
     - 10 (календарні)
   * - clarificationUntilDuration
     - 3 (календарні)
     - 3 (робочі)
   * - qualificationDuration
     - 0
     - 20 (робочі)
   * - minTenderingDuration
     - 15 (календарні)
     - 30 (календарні)
   * - hasEnquiries / minEnquiriesDuration
     - false / 0
     - false / 0
   * - enquiryPeriodRegulation
     - 4 (календарні)
     - 6 (календарні)
   * - restricted
     - false
     - false
   * - hasMultiSourcing
     - false
     - false

Опис кожного поля конфігурації наведено в секції :ref:`config`.

Схеми конфігурації та використання майданчиками
-----------------------------------------------

- схеми конфігурації зберігаються в `standards <https://github.com/ProzorroUKR/standards>`_:
  базова ``data_model/schema/TenderConfig/openTendering.json`` та схеми різновидів
  ``openTendering.UA.json`` / ``openTendering.EU.json`` (значення кожного поля для різновиду, див. таблицю
  вище); окремого API ЦБД для отримання переліку конфігурацій немає (як і для ``competitiveOrdering``);
- майданчик при виборі замовником різновиду бере відповідну схему ``openTendering.<UA|EU>.json`` і формує
  ``config``: фіксовані значення - зі схеми, ``hasAuction`` та ``hasValueRestriction`` - на вибір замовника;
- майданчик передає ``procurementMethodType`` = ``openTendering``, ``procurementMethodSubtype`` = ``UA`` | ``EU``
  та повний ``config``;
- ЦБД валідує ``config`` за базовою схемою та схемою різновиду; значення, що не відповідає різновиду
  (наприклад, ``minTenderingDuration`` = 30 для UA), відхиляється з помилкою 422;
- після створення закупівлі ``procurementMethodSubtype`` та ``config`` змінити не можна (``config`` у
  ``PATCH`` ігнорується).
