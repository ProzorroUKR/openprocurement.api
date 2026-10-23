.. _open_tendering_feature:

Відкриті торги за Законом № 4888 (openTendering)
=================================================

Загальний опис
--------------

Закон України № 4888-IX запроваджує нові відкриті торги. За домовленостями по запуску нових тендерів:

- для нових відкритих торгів створено **окремий** ``procurementMethodType`` - ``openTendering``
  (назва українською - "Відкриті торги");
- один ``procurementMethodType`` охоплює і національні торги (UA), і торги вище європейських порогів (EU);
  різновид задається окремою ознакою в системі - полем тендера ``procurementMethodSubtype``;
- legacy відкриті торги (``aboveThresholdUA``, ``aboveThresholdEU``, ``aboveThreshold``) не змінюються;
- ``aboveThresholdUA`` на UI перейменовується на "Відкриті торги з публікацією українською мовою"
  (зміни на UI, ЦБД не стосується);
- питання щодо ``scheme`` поставлено на паузу.

`Домовленості по запуску <https://prozorro-ua.atlassian.net/browse/CS-22674>`_

`Відкриті торги (бізнес-вимоги) <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/1042186242>`_

`Відмінності відкритих торгів 4888, 922 та 1178 <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/1226276867>`_

Бізнес-логіка
-------------

Різновиди UA та EU
~~~~~~~~~~~~~~~~~~

Під час створення закупівлі замовник обов'язково вказує різновид відкритих торгів полем тендера
``procurementMethodSubtype`` (``UA`` або ``EU``). Різновид визначає значення конфігурації та не може бути
змінений після створення закупівлі (поля немає в моделі ``PATCH``, спроба зміни відхиляється з помилкою
``Rogue field``). Для інших процедур поле не приймається.

Спільне для обох різновидів:

- торги відбуваються навіть з однією поданою пропозицією (``minBidsNumber`` = 1);
- замовник вирішує, чи застосовувати електронний аукціон (``hasAuction``);
- замовник вирішує, чи може ціна пропозиції перевищувати очікувану вартість (``hasValueRestriction``);
- валюта пропозиції має збігатися з валютою очікуваної вартості (``valueCurrencyEquality`` = ``true``,
  як і в інших відкритих процедурах);
- оскарження умов закупівлі, рішення про переможця та скасування працюють за загальними правилами
  (4, 10 та 10 днів відповідно);
- договір укладається не раніше ніж через 10 днів після визначення переможця;
- категорії замовників: усі, крім ``other``.

Оголошення та редагування
~~~~~~~~~~~~~~~~~~~~~~~~~

Закупівля переходить у статус ``active.tendering`` одразу після активації: окремого періоду уточнень немає,
звернення подаються протягом ``enquiryPeriod``, який є частиною ``tenderPeriod``. Замовник може вносити
зміни протягом усього періоду подання пропозицій; після зміни всі подані пропозиції стають ``invalid`` і
потребують повторного підтвердження.

Продовження періоду подання пропозицій після змін:

- зміну закупівлі в статусі ``active.tendering`` дозволено, якщо після неї до ``tenderPeriod.endDate``
  залишається не менше **N повних календарних днів**: UA - N = 4, EU - N = 7;
- день внесення зміни не враховується: відлік ведеться з 00:00 наступного дня;
- якщо днів залишається менше, зміна відхиляється з помилкою ``tenderPeriod should be extended by N days``;
  замовник має в тому самому запиті перенести ``tenderPeriod.endDate`` так, щоб умова виконувалась;
- приклад: зміна 10.11 о 15:00 - для UA ``tenderPeriod.endDate`` має бути не раніше 15.11 00:00
  (повні дні 11, 12, 13, 14), для EU - не раніше 18.11 00:00.

Мова оголошення:

- UA - оголошення українською; англійські поля (``*_en``) не обов'язкові, але не заборонені;
- EU - оголошення додатково публікується англійською, обов'язкові поля: ``procuringEntity.name_en``,
  ``procuringEntity.identifier.legalName_en``, ``procuringEntity.contactPoint.name_en``,
  ``procuringEntity.additionalContactPoints[].name_en``, ``items[].description_en``
  (як в ``aboveThresholdEU``); ``procuringEntity.contactPoint.availableLanguage`` за замовчуванням - ``uk``.

Шаблон договору визначається на рівні тендера: при оголошенні (вихід зі статусу ``draft``) обов'язково
вказується або ``contractTemplateName``, або документ з ``documentType`` = ``contractProforma`` (але не обидва
одночасно); ``contractTemplateName`` можна змінювати у статусах ``draft`` та ``active.tendering``.

Скаргу на умови закупівлі можна подати не пізніше ніж за 4 дні до кінцевого строку подання пропозицій.
Зареєстрована скарга зупиняє перебіг закупівлі (аукціон, розкриття); під час її розгляду замовник не може
скасувати закупівлю чи укласти договір.

Подання пропозицій та торги, що не відбулися
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Кожен учасник подає одну пропозицію протягом періоду подання; резидент накладає підпис. Якщо не подано
жодної пропозиції - закупівля переходить у ``unsuccessful``.

Документи пропозиції подаються за існуючим механізмом конвертів (як в ``aboveThresholdUA`` /
``aboveThresholdEU``) - для обох різновидів доступні ``documents``, ``eligibilityDocuments``,
``financialDocuments``, ``qualificationDocuments``. Видимість документів визначається конфігурацією
``hasPrequalification``:

- UA (``hasPrequalification`` = ``false``) - ``documents`` та ``eligibilityDocuments`` закриті під час
  ``active.tendering`` та ``active.auction``, ``financialDocuments`` та ``qualificationDocuments`` - також до
  завершення аукціону; після аукціону відкриваються всі документи;
- EU (``hasPrequalification`` = ``true``) - на попередній кваліфікації розкриваються ``documents`` та
  ``eligibilityDocuments``, ``financialDocuments`` та ``qualificationDocuments`` - після аукціону.

UA:

- одна пропозиція - аукціон не проводиться, учасник потрапляє на розгляд (``award`` у ``pending``),
  закупівля переходить у ``active.qualification``;
- дві та більше пропозицій та ``hasAuction`` = ``true`` - проводиться аукціон;
- дві та більше пропозицій та ``hasAuction`` = ``false`` - на розгляд потрапляє пропозиція з найнижчою ціною.

EU:

- хоча б одна пропозиція - закупівля переходить у ``active.pre-qualification``;
- після попередньої кваліфікації: допущено дві й більше пропозицій та ``hasAuction`` = ``true`` - аукціон;
  допущено одну пропозицію або аукціон не застосовується - визначення переможця; не допущено жодної -
  ``unsuccessful``.

Попередня кваліфікація (EU)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Пропозиції розкриваються без ціни; по кожному учаснику замовник приймає рішення ``active`` /
``unsuccessful`` та підтверджує ``qualified`` і ``eligible``. На цьому етапі застосовується норма 24 години.
Етап завершується підписанням протоколу (``evaluationReports``), після чого триває період оскарження
10 календарних днів.

Аукціон, АНЦ та визначення переможця
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Аукціон проводиться за наявності ``hasAuction`` = ``true`` та двох і більше (допущених) пропозицій.
Правила аномально низької ціни лишаються загальними для системи, розрахунок більше не прив'язаний до
аукціону. Після ранжування пропозицій замовник визначає переможця або відхиляє пропозицію (із
підтвердженням ``qualified`` / ``eligible``); строк розгляду - 5 робочих днів з продовженням до 20
(milestone ``extensionPeriod``). Milestone ``24h`` на етапі визначення переможця доступний лише в UA.
Період оскарження рішення про переможця - 10 календарних днів.

Скасування та договір
~~~~~~~~~~~~~~~~~~~~~

Скасування закупівлі/лоту - із зазначенням причини, заборонене під час розгляду скарги; період оскарження
скасування - 10 календарних днів. Договір публікується не раніше ніж через 10 днів після визначення
переможця за відсутності нерозглянутих скарг; після активації договору закупівля (лот) переходить у
``complete``. Якщо в тендері обрано шаблон договору (``contractTemplateName``) і майданчики замовника та
постачальника підтримують електронний договір (``contract_owner``), договір проходить за сценарієм
електронного договору.

Конфігурація
~~~~~~~~~~~~

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

Зберігання конфігурацій та використання майданчиками:

- схеми конфігурацій зберігаються в standards: базова ``openTendering.json`` та схеми різновидів
  ``openTendering.UA.json`` / ``openTendering.EU.json`` (значення кожного поля для різновиду, див. таблицю вище);
  окремого API ЦБД для отримання переліку конфігурацій немає (як і для ``competitiveOrdering``);
- майданчик при виборі замовником різновиду бере відповідну схему ``openTendering.<UA|EU>.json`` і формує
  ``config``: фіксовані значення - зі схеми, ``hasAuction`` та ``hasValueRestriction`` - на вибір замовника;
- майданчик передає ``procurementMethodType`` = ``openTendering``, ``procurementMethodSubtype`` = ``UA`` | ``EU``
  (поле обов'язкове; довідник - ``codelists/tender/tender_procurement_method_subtype.json``) та повний ``config``;
- ЦБД валідує ``config`` за базовою схемою та схемою різновиду; значення, що не відповідає різновиду
  (наприклад, ``minTenderingDuration`` = 30 для UA), відхиляється з помилкою 422;
- після створення закупівлі ``procurementMethodSubtype`` та ``config`` змінити не можна.

Технічне рішення
-------------------------------------

Standards
~~~~~~~~~

https://github.com/ProzorroUKR/standards

- ``data_model/schema/TenderConfig/openTendering.json`` - базова схема конфігурації процедури: усі наявні
  поля конфігурації; поля, що відрізняються між різновидами, мають об'єднані переліки значень
  (``minTenderingDuration: [15, 30]``, ``enquiryPeriodRegulation: [4, 6]`` тощо).
- ``data_model/schema/TenderConfig/openTendering.UA.json`` та ``openTendering.EU.json`` - повні схеми
  різновидів, що фіксують по одному значенню кожного поля (за аналогією з ``competitiveOrdering.short`` /
  ``competitiveOrdering.long``).
- ``codelists/tender/tender_procurement_method_type.json`` - новий запис ``openTendering``
  ("Відкриті торги", ``procurementMethod: open``).
- ``codelists/tender/tender_procurement_method_subtype.json`` - довідник значень ``procurementMethodSubtype``
  (``UA`` - "Відкриті торги з публікацією українською мовою", ``EU`` - "Відкриті торги з публікацією англійською
  мовою").
- ``organizations/kind_procurementMethodType_mapping.json`` - ``authority, social, central, general,
  defense, special``.
- ``criteria/rules/openTendering.json`` - копія правил ``aboveThresholdUA`` (критерії за Законом 4888 -
  окрема задача).

API ЦБД
~~~~~~~

Нова процедура обслуговується пакетом ``openprocurement.tender.open`` разом з іншими відкритими
процедурами (спільні моделі ``tender.core``, маршрути з префіксом ``open``).

- ``openprocurement.tender.open.constants`` - ``OPEN_TENDERING``, константи різновидів, строки продовження
  періоду подання (``4`` / ``7`` днів), конфігурації робочих/календарних днів для UA та EU.
- Реєстрація типу: ``OPEN_PROCUREMENT_METHOD_TYPES``, ``CORE_TENDER_PROCUREMENT_METHOD_TYPES``,
  ``FIRST_STAGE_PROCUREMENT_TYPES``, переліки гарантій та обов'язкових ``bid.items``
  (``openprocurement.api.constants``), ``TENDER_CONFIG_JSONSCHEMAS``, ``TENDER_CRITERIA_RULES``,
  планування (``PROCEDURES["open"]``), передача прав (``relocation``), CI job ``test_tender_open_tendering``.
- ``openprocurement.tender.open.procedure.models.tender`` - ``OpenTenderingPostTender`` /
  ``OpenTenderingTender`` з обов'язковим полем ``procurementMethodSubtype`` (``UA`` / ``EU``); модель ``PATCH``
  поля не містить (незмінність), базові моделі ``tender.core`` не змінюються (для legacy процедур поле
  відхиляється як ``Rogue field``). Поле доступне у фіді через ``opt_fields``.
- Вибір різновиду: ``OpenTenderingStateClass`` (``tender/open/procedure/views/base.py``) - резолвер
  стейт-класу за полем ``procurementMethodSubtype`` (при ``POST /tenders`` - з тіла запиту, далі - з тендера).
  Використовується для тендера, лотів, критеріїв та milestones авардів; решта ресурсів мають спільні
  стейт-класи ``OpenTendering*``.
- ``OpenTenderingUATenderDetailsState`` / ``OpenTenderingEUTenderDetailsState`` - відрізняються
  ``extra_config_schema_name`` (``openTendering.UA`` / ``openTendering.EU``), ``tender_period_extra``,
  ``working_days_config``; EU додатково вимагає поля англійською (``EU_REQUIRED_MULTILINGUAL_FIELDS``).
- Валідація конфігурації: базова схема, а потім схема різновиду "поверх" неї (механізм
  ``extra_config_schema_name`` із competitiveOrdering, словник ``TENDER_EXTRA_CONFIG_JSONSCHEMAS``).
  Значення за замовчуванням обираються зі схеми різновиду. Конфігурація незмінна після створення
  (``PATCH`` ігнорує ``config``).
- Перевірки ціни та валюти пропозиції й договору працюють як в інших відкритих процедурах
  (``valueCurrencyEquality`` = ``true``, обмеження ціни - за ``hasValueRestriction``).
- Milestones авардів: UA - ``24h`` та ``extensionPeriod``; EU - лише ``extensionPeriod``
  (``24h`` - на кваліфікаціях).
- Решта поведінки (попередня кваліфікація, оскарження кваліфікації, конверти документів пропозиції,
  АНЦ, мінімальна кількість пропозицій, строки оскаржень) керується конфігурацією в ``tender.core`` і нової
  логіки не потребує.
- Тести: ``tender/open/tests/open_tendering/{ua,eu}`` на основі тестів ``aboveThresholdUA`` /
  ``aboveThresholdEU`` з перевірками, специфічними для openTendering (валідація та незмінність
  ``procurementMethodSubtype``, відхилення поля для legacy процедур, значення різновидів, одна пропозиція).

Відкриті питання та припущення
------------------------------

- Критерії за Законом 4888 - окрема задача; наразі діють правила ``aboveThresholdUA``.
- Строк подання вимог (claims) - 10 днів до кінця подання пропозицій, як у legacy процедурах.
- EU: ``title_en`` та ``description_en`` тендера не обов'язкові (як в ``aboveThresholdEU``); якщо потрібно - треба
  додати їх до ``EU_REQUIRED_MULTILINGUAL_FIELDS``.
- Публічна документація процедури (туторіали UA/EU, опис поля ``procurementMethodSubtype``) буде
  додана після релізу standards та запуску процедури.

Наступні кроки
--------------

- Реліз standards з новими файлами та оновлення версії standards в ЦБД.
- Додати ``openTendering`` до модуля аукціонів (за потреби) та перевірити інтеграції.