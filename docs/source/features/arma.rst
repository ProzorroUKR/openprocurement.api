АРМА
====

Етап 1: Складний актив
----------------------

Загальний опис
~~~~~~~~~~~~~~

- Створити новий тип закупівлі (``procurementMethodType``) на основі aboveThresholdEU.
- Налаштувати обмеження конфігурацій. Відключити непотрібну функціональність.
- Реалізувати новий тип ``value`` для проведення тендеру по розміру винагороди (у відсотках).

`Закупівля АРМА (загальна інформація) <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/578715650>`_

`Процес відбору управителя складних активів <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/594870280>`_

`Різниця між структурами тендеру простого активу та складного активу <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/637698053>`_

Загальний план
~~~~~~~~~~~~~~

API ЦБД
"""""""

- Створити новий тип тендера

  - Створити новий модуль тендерінгу з новим ``procurementMethodType`` (див. нижче)
  - Налаштувати для нового типу процедури словники standards (див. нижче)
  - Відключити непотрібну функціональність (див. нижче)
  - Реалізувати новий тип поля ``value`` (див. нижче)

    - Нова структура поля ``value`` (див. нижче)
    - Робота аукціону з новою структурою поля ``value`` (див. нижче)

  - Відключити нецінові критерії (див. нижче)
  - Відключити життєвий цикл (див. нижче)
  - Заборонити використання ``contractTemplateName`` (див. нижче)
  - Адаптувати логіку роботи milestones (див. нижче)
  - Повний набір тестів процедури по аналогії з іншими типами процедур

- Налаштувати роботу контрактів

  - Реалізувати роботу з новим типом поля ``value``

    - Створення контракту
    - Оновлення контракту
    - Зміни до контракту

  - Змінити логіку роботи ``amountPaid``
  - Тести для нового типа поля ``value``

- Оновлення документації

  - Структура нового ``value``
  - Туторіал нової процедури

Модуль аукціонів
~~~~~~~~~~~~~~~~

Додати новий procurementMethodType в модуль аукціонів

ЦБД - Створити новий модуль тендерінгу з новим ``procurementMethodType``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Створити новий модуль тендерінгу з новим ``procurementMethodType`` на основі модуля openeu (aboveThresholdEU)

Standards - Налаштувати для нового типу процедури словники
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Налаштувати конфігурації для створення процедури відповідно до ТЗ
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

https://github.com/ProzorroUKR/standards/tree/master/data_model/schema/TenderConfig

`Процес відбору управителя складних активів <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/594870280>`_

2. Налаштувати перелік критеріїв
""""""""""""""""""""""""""""""""

Обов'язкових критеріїв немає тому зробити пустим масивом

https://github.com/ProzorroUKR/standards/tree/master/criteria/rules

`Процес відбору управителя складних активів <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/594870280>`_

`Різниця між структурами тендеру простого активу та складного активу <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/637698053>`_

Деякі валідації критеріїв можуть потребувати змін в цбд.

3. Налаштувати перелік дозволених типів організацій
"""""""""""""""""""""""""""""""""""""""""""""""""""

https://github.com/ProzorroUKR/standards/blob/master/organizations/kind_procurementMethodType_mapping.json

Перелік значень для нового типу процедури

.. code-block:: json

   [
     "authority"
   ]

Адаптація функціоналу
~~~~~~~~~~~~~~~~~~~~~

`Процес відбору управителя складних активів <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/594870280>`_

`Різниця між структурами тендеру простого активу та складного активу <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/637698053>`_

1. Відключити обов'язковість ``tender.milestones``
""""""""""""""""""""""""""""""""""""""""""""""""""

Відключити обов'язковість ``tender.milestones`` (і відповідно ``contract.milestones``) з типами:

- delivery
- financing

.. code-block:: python

   def validate_milestones(self, data, value):
       if tender_created_after(MILESTONES_VALIDATION_FROM):
           if value is None or len(value) < 1:
               raise ValidationError("Tender should contain at least one milestone")

2. Адаптація ``award.milestones``
"""""""""""""""""""""""""""""""""
Функціональність майлстоунів для нової процедури аналогічна стандартній функціональності майлстоунів за виключенням того що:

- alp ``dueDate`` має бути через 2 робочих дні після спрацювання
- прибрати ``extensionPeriod`` з допустимих значень для ``award.milestones.сode``

3. Заборонити використання ``tender.contractTemplateName``
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Заборонити встановлення значення для поля ``contractTemplateName`` на етапі створення тендера.

4. Заборонити використання ``tender.features``
""""""""""""""""""""""""""""""""""""""""""""""

Нецінові критерії не будуть застосовуватися. Заборонити встановлення значення для поля ``tender.features`` на етапі створення тендера.

5. Встановити тип ``tender.awardCriteria``
""""""""""""""""""""""""""""""""""""""""""

Дозволити тільки ``ratedCriteria`` в полі ``tender.awardCriteria``

6. Додатково дозволити замовнику додавати документи
"""""""""""""""""""""""""""""""""""""""""""""""""""

Додавання документів будь якого ``documentType`` з існуючого списку відповідно батьківської сутності (tender/award/contract) + документ без вказання ``documentType``:

- ``tender.status=draft`` >> дозволити додавати ``tender.documents``
- ``tender.status=active.tendering`` >> дозволити додавати ``tender.documents``
- ``tender.status=active.pre-qualification`` >> дозволити додавати ``tender.documents``
- ``tender.status=active.qualification`` >> дозволити додавати ``award.documents``
- ``tender.status=active.awarded`` >> дозволити додавати ``award.documents``
- ``contract.status=pending/active`` >> дозволити додавати ``contract.documents``

Розробка нової структури поля value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1 фаза:

- тендерінг
- подання пропозицій
- деактивація аукціону (``hasAuction`` = false)

2 фаза:

- аукціон (``hasAuction`` = true)

3 фаза:

- контрактінг

4 фаза:

- вартість активу
- білінг

----

Адаптація полів системи для процедури АРМА:

- ``tender.value`` - delete
- ``tender.minimalStep`` - delete
- ``tender.guarantee`` - leave as is
- ``tender.lots[].value`` - new structure
- ``tender.lots[].minimalStep`` - new structure
- ``tender.lots[].guarantee`` - leave as is
- ``tender.bids[].value`` - leave as is
- ``tender.bids[].lotsValues[].value`` - new structure
- ``tender.bids[].items[].unit.value`` - leave as is
- ``tender.items[].unit.value`` - leave as is
- ``tender.awards[].value`` - new structure
- ``tender.awards[].items[].value`` - leave as is
- ``contract.value`` - new structure

Структура
"""""""""

- Інша назва поля по аналогії з esco.
- Прибрати поля ``currency``, ``valueAddedTaxIncluded``.

.. code-block:: json

   {
       "value": {
           "amountPercentage": 30.5
       }
   }

Валідації
"""""""""

1. Валідації для ``tender.lots[].value``:

- ``tender.lots[].value.amountPercentage`` >= 0
- ``tender.lots[].value.amountPercentage`` <= 100

2. Валідації для ``tender.lots[].minimalStep``:

- ``tender.lots[].minimalStep.amountPercentage`` >= 0
- ``tender.lots[].minimalStep.amountPercentage`` <= ``tender.lots[].value.amountPercentage``

3. Валідації для ``tender.bids[].lotValues[].value``:

- ``tender.bids[].lotValues[].value.amountPercentage`` >= 0
- ``tender.bids[].lotValues[].value.amountPercentage`` <= ``tender.lots[].value.amountPercentage`` (``tender.lots[].value.amountPercentage`` - верхній поріг в ставках)

4. Валідації для ``contract.value``:

- ``contract.value.amountPercentage`` >= 0
- ``contract.value.amountPercentage`` <= ``tender.awards[].value.amountPercentage``

5. Перевірити/адаптувати всі інші валідації що використовували поля:

- ``value.amount``
- ``value.amountNet``
- ``value.currency``
- ``value.valueAddedTaxIncluded``

Авардінг
""""""""

Реалізувати визначення переможної пропозиції за полем ``tender.awards[].value.amountPercentage``

.. code-block:: python

   awarding_criteria_key: str = "amountPercentage"

Аномально низька ціна (ALP)
"""""""""""""""""""""""""""

Налаштувати розрахунок аномально низької ціни за полем ``tender.awards.value.amountPercentage`` використовуючи значення ``awarding_criteria_key``:

Розрахунок ``weightedValue``
""""""""""""""""""""""""""""

Поле ``weightedValue`` створюється на основі поля ``value`` якщо в тендері використовується неціновий критерій або життєвий цикл.
Оскільки нецінові критерії та життєвий цикл не будуть застосовуватися, поле ``weightedValue`` не буде створюватися.

Але пропонується адаптувати його роботу за полем ``tender.awards.value.amountPercentage`` використовуючи значення ``awarding_criteria_key``, на випадок якщо вищеописана функціональність буде застосована в майбутньому.

Тобто для ``value``:

.. code-block:: json

   {
       "value": {
           "amountPercentage": 30.5
       }
   }

Генерувати (якщо вимагається умовами проведення тендера що описані вище) ``weightedValue``:

.. code-block:: json

   {
       "weightedValue": {
           "amountPercentage": 30.5,
           "addition": 0.0,
           "denominator": 1
       }
   }

Аукціон
"""""""

Реалізувати двусторонню конвертацію ``value`` (а також ``weightedValue`` за наявності) з старого формату в новий і в зворотньому напрямку.

Етап імпорту тендеру датабріджом аукціонів
''''''''''''''''''''''''''''''''''''''''''

ЦБД розуміючи що запит від модуля аукціону у відповіді переформатовує всі value. Використовуючи поле currency для позначення відсотків.

Наприклад (``weightedValue`` теж переводити)

.. code-block:: json

   {
       "value": {
           "amountPercentage": 30.5
       }
   }

Конвертувати в:

.. code-block:: json

   {
       "value": {
           "amount": 30.5,
           "currency": "%"
       }
   }

Етап звітування аукціоном про результати
''''''''''''''''''''''''''''''''''''''''

В ендпоінті ЦБД для аукціону робити зворотню конвертацію


Етап 2: Простий актив
----------------------

Загальний опис
~~~~~~~~~~~~~~

Створити новий тип відбору (``frameworkType``) та його похідних на основі internationalFinancialInstitutions. Налаштувати обмеження конфігурацій. Відключити непотрібну функціональність.

Створити новий тип закупівлі (``procurementMethodType``) на основі процедури складних активів. Налаштувати обмеження конфігурацій. Відключити непотрібну функціональність. Використати вже ралізований в складних активах новий тип ``value`` для проведення тендеру по розміру винагороди (у відсотках).

`Закупівля АРМА (загальна інформація) <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/578715650>`_

`Процес відбору управителя простих активів <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/607780865>`_

`Різниця між структурами тендеру простого активу та складного активу <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/637698053>`_

Загальний план
~~~~~~~~~~~~~~

API ЦБД
"""""""

- Створити новий тип відбору

  - Створити новий модуль в frameworks з новим ``frameworkType`` (див. нижче)
  - Зареєструвати модуль в ``pyproject.toml``
  - Налаштувати для нового типу відбору словники standards (див. нижче)
  - Відключити непотрібну функціональність (див. нижче)
  - Доробити періоди

- Створити новий тип тендера

  - Створити новий вид тендерінгу з новим ``procurementMethodType`` в модулі arma (див. нижче)
  - Налаштувати для нового типу процедури словники standards (див. нижче)
  - Відключити непотрібну функціональність (див. нижче)
  - Налаштувати зв'язок з відбором через ``agreement`` (див. нижче)
  - Використати новий тип поля ``value`` (наслідуємо зі складних активів)
  - Додати нецінові критерії (`tender.features`)
  - Відключити життєвий цикл (наслідуємо зі складних активів)
  - Заборонити використання ``contractTemplateName`` (наслідуємо зі складних активів)
  - Адаптувати логіку роботи milestones (див. нижче)
  - Повний набір тестів процедури по аналогії з іншими типами процедур

- Налаштувати роботу контрактів

  - Використати роботу з новим типом поля ``value`` зі складних активів
  - Заборонити створювати електронний контракт

- Оновлення документації

  - Туторіал нової процедури

Модуль аукціонів
~~~~~~~~~~~~~~~~

Додати новий procurementMethodType в модуль аукціонів

Billing
~~~~~~~~

Додати новий procurementMethodType в білінг

ЦБД - Створити новий модуль відбору з новим ``frameworkType``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Створити новий тип відбору (``frameworkType``) на основі internationalFinancialInstitutions.
Назва: `assetRecoveryManagementAgency`.

Стейт класи краще унаслідувати з `core`, менше пропертів треба буде перевизначати.

Standards - Налаштувати для нового типу відбору словники
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Налаштувати конфігурації для створення відбору відповідно до ТЗ
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

https://github.com/ProzorroUKR/standards/tree/master/data_model/schema/FrameworkConfig

Адаптація функціоналу
~~~~~~~~~~~~~~~~~~~~~

Додати обов'язковий підпис рішення по кваліфкації:

.. code-block:: python

    evaluation_reports_doc_required = True

Вимкнути функціонал перевірки мінімальної кількості учасників для успішного відбору:

.. code-block:: python

    min_submissions_number = 0
    min_submissions_number_days = 0  # щоб вимкнути перехід відбору у unsuccessful

``get_next_check`` для ``active``-відбору завжди додає ``qualificationPeriod.endDate``, тому хронограф переведе відбір у ``complete``, коли прийде час.

Доробити періоди
~~~~~~~~~~~~~~~~~

Період уточнення має тривати стільки же, скільки період поданя заявок і закінчуватися за 30 к.д. до періоду розгляду заявок (`qualificationPeriod.endDate - 30 к. д.`).

Додати нову проперті на рівні стейт класу, яка буде вмикати безтерміновий період уточнення:

.. code-block:: python

    enquiry_period_lasts_until_qualification = False

https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/607780865#%D0%9F%D0%B5%D1%80%D1%96%D0%BE%D0%B4%D0%B8

ЦБД - Створити новий вид тендерінгу з новим ``procurementMethodType``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Додати в модуль тендерінгу arma новий ``procurementMethodType`` для простих активів (`simpleAsset.arma`).

Структура в'юх
""""""""""""""

За приклад беремо модуль ``tender/open``, де в одному модулі живуть вісім ``procurementMethodType``: один ``@resource`` зі списком PMT і словник ``state_classes``, з якого ``TenderBaseResource.get_state_class`` обирає стейт за PMT запиту.

.. code-block:: python

   @resource(
       name=f"{ARMA_ROUTE_PREFIX}:Tenders",
       collection_path="/tenders",
       path="/tenders/{tender_id}",
       procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
       description="ARMA tenders",
       accept="application/json",
   )
   class ARMATendersResource(TendersResource):
       serializer_class = TenderBaseSerializer
       state_classes = {
           COMPLEX_ASSET_ARMA: ARMATenderDetailsState,
           SIMPLE_ASSET_ARMA: SimpleAssetTenderDetailsState,
       }


Standards - Налаштувати для нового типу процедури словники
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Налаштувати конфігурації для створення процедури відповідно до ТЗ
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

https://github.com/ProzorroUKR/standards/tree/master/data_model/schema/TenderConfig

2. Налаштувати перелік критеріїв
""""""""""""""""""""""""""""""""

Обов'язкових критеріїв немає тому зробити пустим масивом

https://github.com/ProzorroUKR/standards/tree/master/criteria/rules

3. Налаштувати перелік дозволених типів організацій
"""""""""""""""""""""""""""""""""""""""""""""""""""

https://github.com/ProzorroUKR/standards/blob/master/organizations/kind_procurementMethodType_mapping.json

Перелік значень для нового типу процедури

.. code-block:: json

   [
     "authority"
   ]

Адаптація функціоналу
~~~~~~~~~~~~~~~~~~~~~

1) Вимкнути функціонал прекваліфікацій (на відміну від складних активів):

.. code-block:: python

   {"hasPrequalification": False}

2) Додати в модель тендера `TenderFeaturesMixin` (нецінові критерії)

Приведена ціна (``weightedValue``) рахується за наявною в системі формулою, нічого нового реалізовувати не треба.
Механізм вмикається автоматично, щойно в тендері з'являються нецінові критерії: хронограф на завершенні ``active.tendering`` рахує ``weightedValue`` для кожної ставки.

.. code-block:: python

   awarding_criteria_key = "amountPercentage"
   weighted_value_with_currency = False

3) Налаштувати зв'язок з відбором:

В модель тендеру додати:

.. code-block:: python

   agreement = ModelType(AgreementUUID, required=True)

Конфіг:

.. code-block:: python

   hasPreSelectionAgreement: true

Стейт клас:

.. code-block:: python

   agreement_field = "agreement"
   agreement_allowed_types = [ARMA_FRAMEWORK_TYPE]
   agreement_min_active_contracts = 2
   should_match_agreement_procuring_entity = True

4) Обмежити статуси, які замовник може виставити через PATCH:

.. code-block:: python

   patch_status_choices = ("draft", "active.tendering")

Що не переносимо зі складного активу
""""""""""""""""""""""""""""""""""""

- Питання (``views/question.py``, ``state/question.py`` і пов'язані константи) — періоду уточнення в тендері немає, питання живуть на рівні відбору.
- Усі ``qualification_*`` в'юхи і стейти (у простого актива ``hasPrequalification: False``).

Адаптація ``award.milestones``
"""""""""""""""""""""""""""""""""
Функціональність майлстоунів для нової процедури аналогічна стандартній функціональності майлстоунів за виключенням того що:

- alp ``dueDate`` має бути через 1 робочий день після спрацювання
- прибрати ``extensionPeriod`` та ``24h`` з допустимих значень для ``award.milestones.сode``

Так як ``extensionPeriod`` та ``24h`` не застосовується, то прибираємо в'юхи і стейти для ``award_milestones``.

Етап 3: Білінг
--------------

Загальний опис
~~~~~~~~~~~~~~

Реалізувати нову логіку білінгу.

`Розрахунок білінгу АРМА <https://prozorro-ua.atlassian.net/wiki/spaces/Knowledge/pages/637960193>`_

Етап 4: Інтеграції
------------------

Інтеграції не передбачені в першій ітерації, але необхідно переконатися що вони не вимагають поля ``value.currency`` або ``value.amount`` в стандартному форматі або адаптувати їх роботу для нового типу ``value``.

Потенційно необхідні інтеграції:

- ЄДР
- ДФС
- НАЗК