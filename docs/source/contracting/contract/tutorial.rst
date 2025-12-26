.. _contracting_tutorial:

Туторіал
========

Розглянемо основні правила
--------------------------

Подивимось як працює точка входу `/contracts`:

.. http:example:: http/contracts-listing-0.http
   :code:

При виклику видає пустий набір.

Перенесення договору із системи закупівель відбувається автоматично.Обставини за яких вібувається перенесення, описані нижче.


.. index:: Contracts

Створення договору
------------------

Нехай у нас відбулась закупівля і є переможець. Після вибору перможця **автоматично** створюється контракт в закупівлі з обмеженим набором полів(`id`, `awardID`, `status`, `date`, `value`) та в системі договорів з повним набором полів(:ref:`Econtract`) у статусі ``pending``.

*Майданчики (брокери) не мають можливості створювати договори в системі договорів.*

Договір створюється з додатковими полями:

* `contractTemplateName` - копіюється з закупівлі, якщо вона встановлена (більше про це в :ref:`contract-template-name`)

Договір PQ створюється з додатковими полями:

* `attributes` - формується з вимог та відповідей на виомги у закупівлі


Отримання договору
------------------

Договір в системі закупівель

.. http:example:: http/example_contract.http
   :code:

*Ідентифікатор `id` договору однаковий в системах закупівель та договорів.*

Спробуємо доступитись до URL створеного об’єкта:

.. http:example:: http/contract-view.http
   :code:


Отримання доступу
-----------------

**ЗАСТЕРЕЖЕННЯ:** Наразі цей метод є застарілим(пізніше буде видаленим), ви можете проводити всі дії над договором використовуючи ``tender_token``.


Для того, щоб отримати права для майбутнього редагування договору, необхідно використати таку в’юшку ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}`` з API ключем майданчика, де була згенерована закупівля.

В ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}``:

* ``id`` - це ідентифікатор договору,

* ``tender_token`` - це токен закупівлі (використовується для генерування токена договору).

У відповіді буде ``access.token`` для договору, який буде використовуватись для модифікації договору.

.. http:example:: http/deprecated-contract-credentials.http
   :code:

Переглянемо договори.

.. http:example:: http/contracts-listing-1.http
   :code:


Ми бачимо внутрішнє `id` договору (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/contracts/`) та його dateModified дату.


Редагування чернетки договору
-----------------------------

Коли договір у статусі `pending` замовник може змінити такі поля:

* `title`
* `description`
* `status`
* `items`
* `value`
* `contractNumber`
* `dateSigned`
* `period`
* `implementation`
* `milestones`


Встановлення вартості договору
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

За замовчуванням вартість договору встановлюється на основі рішення про визначення переможця, але є можливість змінити це значення.

Якщо ви хочете **знизити вартість договору**, ви можете встановити нове значення для поля `amount` або `amountNet` (для всіх процедур окрім esco).

.. http:example:: http/contract-set-contract-value.http
   :code:

Було повернуто код відповіді `200 OK`. Значення змінено успішно.

Встановлення ціни за одиницю
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: http/contract-set-contract_items_unit-value.http
   :code:

`200 OK` відповіддь повертається з успішно створеною структурою item.unit.value.

`Item.unit.value.currency` має відповідати значенню `contract.value.currency`. `Item.unit.value.valueAddedTaxIncluded` має бути `False`.


Встановлення дати підписання договору
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Є можливість встановити дату підписання договору. Для цього вставте відповідну дату в поле `dateSigned`.

Якщо ви не встановите дату підписання, то вона буде згенерована автоматично під час реєстрації договору.

.. http:example:: http/contract-sign-date.http
   :code:

Встановлення терміну дії договору
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Встановлення терміну дії договору необов’язкове, але, якщо є необхідність, ви можете встановити відповідну дату початку `startDate` та кінця `endDate` терміну дії.

.. http:example:: http/contract-period.http
   :code:

Завантаження документації по договору
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Документи пов’язані з договором можна завантажувати лише до контракту у статусі `pending` чи `active`. Спробуємо додати такий документ:

.. http:example:: http/contract-upload-document.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів, щоб підтвердити дію:

Переглянемо список завантажених документів:

.. http:example:: http/contract-get-documents.http
   :code:

Тепер спробуємо додати ще один документ щодо укладанням договору:

.. http:example:: http/contract-upload-second-document.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що ще один документ було додано.

Тепер переглянемо знову усі документи пов’язані із укладанням договору:

.. http:example:: http/contract-get-documents-again.http
   :code:


Скасування договору
-------------------

Існує два способи скасування договору:

* Зміна стаусу award з `active` на `cancelled`
* Зміна статусу договору з "pending" to "cancelled" (цей метод працює, коли це не останній активний договір)


.. _contracting_tutorial_cancelling_award:

Відміна договору через award
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Все що потрібно, це змінити статус award на ``cancelled``

.. http:example:: http/award-cancelling.http
   :code:

Договір у системі закупівель **автомтично** перейде до ``cancelled``

.. http:example:: http/tender-contract-cancelled.http
   :code:

Договір у системі договорів також **автоматично** перейде до ``cancelled``

.. http:example:: http/contract-cancelled.http
   :code:

Відміна через зміну договору
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо ви спробуєте змінити статус договору з ``pending`` на ``cancelled`` ви отримаєте помилку:

.. http:example:: http/contract-cancelling-error.http
   :code:


Активація договору
------------------

Якщо у закупівлі встановлено `contractTemplateName` (більше про це в :ref:`contract-template-name`), то це значення буде використано як `contractTemplateName` для договору. Якщо `contractTemplateName` встановлено для договору, то для його активації потрібна інформація про підписантів. Розглянемо закупівлю з встановленим `contractTemplateName`:

.. http:example:: http/tender-with-contract-template-name.http
   :code:


При спробі активувати договір без заповненої інформації підписанта, буде отримана помилка:

.. http:example:: http/contract-activating-error.http
   :code:


Замовник заповнює інформацію підписанта використовуючи ``contract_token`` чи ``tender_token``:

.. http:example:: http/contract-owner-add-signer-info.http
   :code:


Постачальник заповнює інформацію підписанта використовуючи ``bid_token``, для `limited` процедури цей запит виконує замовник використовуючи ``contract_token`` чи ``tender_token``:

.. http:example:: http/contract-supplier-add-signer-info.http
   :code:


Інформацію підписанта можна оновоити використовуючи той самий спосіб:

.. http:example:: http/update-contract-owner-add-signer-info.http
   :code:

При спробі активувати договір без заповненої обов'язкової інформації, буде отримана помилка:

.. http:example:: http/contract-activating-error-fields.http
   :code:

Після того, як було додано інформацію про підписантів та інші обов'язкові поля, ви можете зареєструвати договір:

.. http:example:: http/contract-activate.http
   :code:


Після активації договору, договір у системі закупівель **автоматично** перейде у `active` і закупівля у статус `complete`:

.. http:example:: http/tender-complete.http
   :code:

Редагування зареєстрованого договору
------------------------------------

Внесення змін до істотних умов договору можливі у випадках, описаних частиною четвертою статті 36 Закону України “Про публічні закупівлі”.

**Істотні умови договору** можуть бути змінені поданням нового об’єкта :ref:`change` в котейнер `Contract.changes`.

Всі зміни `change` обробляються точкою входу (endpoint) `/contracts/{id}/changes`.

Подання зміни
~~~~~~~~~~~~~

Додамо нову зміну `change` до договору:

.. http:example:: http/add-contract-change.http
   :code:

Зверніть увагу на те, що ви можете надати більше ніж одне значення для поля ``rationaleTypes``.

Можливі значення для поля `rationaleTypes` валідуються зі списку причин, вказаних в  `contractChangeRationaleTypes`.

Якщо буде вказана причина, якої немає в  `contractChangeRationaleTypes`, ми побачимо помилку:

.. http:example:: http/add-contract-change-invalid-rationale-types.http
   :code:

Ви можете переглянути зміну `change`:

.. http:example:: http/view-contract-change.http
   :code:

Зміну `change` можна модифікувати доки вона має статус ``pending``.

.. http:example:: http/patch-contract-change.http
   :code:

Завантаження документа зміни
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Документ можна додати доки зміна `change` має статус ``pending``.

Документ додається в два етапи:

* ви повинні завантажити документ

.. http:example:: http/add-contract-change-document.http
   :code:

* ви повинні задати властивості документа: ``"documentOf": "change"`` та ``"relatedItem": "{change.id}"``, щоб "прив’язати" завантажений документ до зміни `change`:

.. http:example:: http/set-document-of-change.http
   :code:

Оновлення властивостей зміни
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Тепер ви можете оновити властивості договору, що стосуються зміни.

Ви можете встановити нові значення для полів `amount` та `amountNet` керуючись наступними правилами:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - `valueAddedTaxIncluded`
     - `Validation`
   * - true
     - Amount should be greater than amountNet and differ by no more than 20%

       (але Amount та amountNet можуть бути рівними)
   * - false
     - Amount and amountNet should be equal


.. http:example:: http/contracts-patch.http
   :code:

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Поля, які можна модифікувати: `title`, `description`, `status`, `value.amount`, `value.amountNet`, `period`, `items`, `amountPaid.amount`, `amountPaid.amountNet`, `terminationDetails`.

Дивіться приклади зміни елемента (`items`) нижче. Ви можете:

* оновити елемент (`items`):

.. http:example:: http/update-contract-item.http
   :code:

* додати новий item:

Дозволяється додавати новий item, але при цьому основні поля мають відповідати попереднім значенням в масиві `items`.

Поля, які не можна змінювати:

* `classification`
* `relatedLot`
* `relatedBuyer`
* `additionalClassifications`

Спробуємо додати новий `item` з новим полем `classification` і побачимо помилку:

.. http:example:: http/add-item-invalid-classification.http
    :code:

Наприклад, розділимо перший `item` на дві номенклатури з такими самими основними полями.

Але при цьому все ще існує валідація на суму цін за одиницю для всіх `items`:

.. http:example:: http/add-item-invalid-price.http
    :code:

Відредагуємо `quantity` в першому `item` і додамо новий `item` з коректною ціною `unit.value`:

.. http:example:: http/add-contract-item.http
   :code:

Застосування зміни
~~~~~~~~~~~~~~~~~~

Зміна `change` застосовується при переключенні в статус ``active``.

Щоб застосувати статус ``active`` потрібно встановити поле `dateSigned`.

Після цього модифікувати зміну `change` вже не можна.

.. http:example:: http/apply-contract-change.http
   :code:

Валідація поля `dateSigned`:

* для першої зміни `change` договору дата повинна бути після `contract.dateSigned`;

* для всіх наступних змін `change` договору дата повинна бути після попередньої дати `change.dateSigned`.

Ви можете переглянути всі зміни:

.. http:example:: http/view-all-contract-changes.http
   :code:

Всі зміни присутні при перегляді контракту.

.. http:example:: http/view-contract.http
   :code:


Завантаження документації
-------------------------

Замовник може завантажити PDF файл у створений договір. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: http/upload-contract-document.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів, щоб підтвердити дію:

.. http:example:: http/contract-documents.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: http/upload-contract-document-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: http/upload-contract-document-3.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: http/get-contract-document-3.http
   :code:


.. index:: Enquiries, Question, Answer


Завершення договору
-------------------

Перед завершенням договору необхідно встановити значення поля  ``amountPaid`` (незалежно від того успішний договір чи ні). Договір можна завершити переключенням у статус ``terminated``. Виконаємо ці дії єдиним запитом:

.. http:example:: http/contract-termination.http
   :code:

Зверніть увагу, що ви можете встановлювати/змінювати значення ``amountPaid.amount``, ``amountPaid.amountNet``, ``amountPaid.valueAddedTaxIncluded``. А значення поля ``amountPaid.currency`` генеруються з поля ``Contract.value``.

Якщо договір неуспішний, то потрібно вказати причини його припинення ``terminationDetails``.

Після цього додання змін до договору не дозволяється.


.. index:: Агреговані контракти

Агреговані контракти
====================

Створення агрегованих контрактів
--------------------------------

Для кожного об'єктку `buyer` в тендері система створює окремий `contract` відповідно, в той момент коли `award` стає активним.

Створюємо тендер з декількома buyers, кожен `item` повинен бути прив'язаний до відповідного `buyer`, використовючи поле `relatedBuyer`:

.. http:example:: http/create-multiple-buyers-tender.http
    :code:

Йдемо далі, як зазвичай, активуємо авард

.. http:example:: http/set-active-award.http
    :code:

Після активації аварду система створює таку кількість об'єктів contracts, що відповідає кількості buyers в тендері

.. http:example:: http/get-multi-contracts.http
    :code:

Оновлюємо Amount.Value для кожного контракту, враховуючи суму добутків Unit.Value на Quantity для кожного item в контракті:

.. http:example:: http/patch-1st-contract-value.http
    :code:

.. http:example:: http/patch-2nd-contract-value.http
    :code:

Ви можете активувати або термінувати кожен контракт як зазвичай. Якщо відсутні контракти в стутусі `pending` та хоча б один котракт знаходиться в статусі `active`, тендер переходить в статус `complete`

При скасуванні аварду всі контракти відповідного awardID переходять в статус cancelled.


Відміна агрегованих контрактів
------------------------------

Контракт може бути відмінений:

.. http:example:: http/patch-to-cancelled-1st-contract.http
    :code:

За винятком коли котракт є останнім невідміненим контрактом:

.. http:example:: http/patch-to-cancelled-2nd-contract-error.http
    :code:

В цьому випадку повинен бути відмінений відповідний авард:

.. http:example:: http/award-cancelling.http
    :code:

Перевіримо що всі контракти відмінені:

.. http:example:: http/get-multi-contracts-cancelled.http
    :code:
