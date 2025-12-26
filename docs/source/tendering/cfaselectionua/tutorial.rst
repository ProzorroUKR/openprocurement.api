.. _cfaselection_tutorial:

Туторіал
========

.. index:: Tender

Configuration
-------------

Набір можливих значень конфігурації:

.. csv-table::
   :file: csv/config.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Набір можливих значень `procuringEntity.kind` для `closeFrameworkAgreementSelectionUA`
--------------------------------------------------------------------------------------

.. csv-table::
   :file: csv/kind.csv
   :header-rows: 1

Створення закупівлі
-------------------

Створимо закупівлю з мінімально допустимим (обовязковим для заповнення) набором даних:

.. http:example:: tutorial/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу на `procurementMethodType`, а також на те, що закупівля створюється зі статусом `draft`.


Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату.

Попередня закупівля була створена лише з обов’язковими полями. Тепер додамо закупівлю з максимально допустимим набором даних при створенні (тендер повинен бути у статусі `created`):

.. http:example:: tutorial/create-tender-procuringEntity.http
   :code:

І знову код відповіді `201 Created`,  заголовок `Location` і тіло з додатковим `id`, `tenderID`, та властивість `dateModified`.

Для того, щоб перейти далі, треба змінити статус процедури на ``draft.pending``. Це дозволить боту наповнити :ref:`Agreement_cfaua` і перевести тендер у наступний статус. Якщо надана інформація відповідає всім вимогам, бот переводить процедуру в статус ``active.enquiries``, інакше в статус ``draft.unsuccessful``.

.. http:example:: tutorial/tender-switch-draft-pending.http
   :code:

Бачимо, що наш тендер відповідає всім вимогам, бот наповнив :ref:`Agreement_cfaua` і змінив статус тендера на ``active.enquiries``.

.. http:example:: tutorial/tender-in-active-enquiries.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: tutorial/initial-tender-listing.http
   :code:

При створенні процедури в статусі `draft`, можна заповнювати наступні поля:
   * у :ref:`Agreement_cfaua` - `id`
   * у :ref:`Tender` - `title`, `title_en`, `description`, `description_en`, `guarantee`, `procurementMethodType`, `procuringEntity`
   * у :ref:`Lot` - `title`, `title_en`, `description`, `description_en`, `id`, `guarantee`
   * у :ref:`Item` - `description`, `quantity`, `relatedLot`, `unit`, `description_en`, `classification`, `additionalClassifications`, `deliveryAddress`, `deliveryDate`, `deliveryLocation`, `id`

Єдине поле, яке можна редагувати :ref:`Tender`: `status`.


Модифікація закупівлі
---------------------



Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: tutorial/tender-listing-after-patch.http
   :code:

Замовник може встановити забезпечення тендерної пропозиції:

.. http:example:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

Можна редагувати наступні поля на цьому етапі процедури:
   * у :ref:`Tender` - `title`, `title_en`, `description`, `description_en`, `tenderPeriod`: `endDate`
   * у :ref:`Lot` - `title`, `description`, `title_en`, `description_en`, `minimalStep`, `amount`
   * у :ref:`Item` - `description`, `description_en`, `deliveryAddress`, `deliveryDate`, `quantity`
   * :ref:`BasicValue`

Різниця між `tenderPeriod`:`endDate` і датою публікації тендера має бути не менше трьох днів.

Можливість редагувати ці залишається, якщо задано декілька :ref:`Item`.


Завантаження документів
-----------------------

Замовник має завантажувати тільки ЕЦП на цьому етапі процедури.

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: tutorial/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ додано:

.. http:example:: tutorial/tender-documents.http
   :code:

Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: tutorial/upload-award-criteria.http
   :code:

І знову можна підтвердити, що два документи завантажені.

.. http:example:: tutorial/tender-documents-2.http
   :code:

Додамо новий `documentType` з пареметром `technicalSpecifications` до попередньо завантаженого документа:

.. http:example:: tutorial/tender-document-add-documentType.http
   :code:

Успіх! Код відповіді `200 OK` і це підтверджує, що поле `documentType` з параметром `technicalSpecifications` було додано.

Тепер спробуємо відредагувати будь-яке поле в документі. Наприклад, `description`:

.. http:example:: tutorial/tender-document-edit-docType-desc.http
   :code:

Було повернуто код відповіді `200 OK`. Значення змінено успішно.

У випадку помилки, можна заново завантажити документ поверх старої версії:

.. http:example:: tutorial/update-award-criteria.http
   :code:

І можна побачити, що цей документ переважає оригінальну версію:

.. http:example:: tutorial/tender-documents-3.http
   :code:


.. index:: Bidding


Реєстрація пропозиції
---------------------

Покроковий режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Коли приходить ``Tender.tenderingPeriod.startDate``, Закупівля отримує статус `active.tendering`, що дозволяє реєстрацію пропозицій.

Учасник може зареєструвати пропозицію у статусі `draft` (чернетка):

Неможливо подати ставку зі значенням вищим, ніж ``agreement.contract.value``. Також, постачальник не може подати ставку, якщо він не є учасником цієї Рамкової угоди (:ref:`Agreement_cfaua`).


.. http:example:: tutorial/register-bidder-invalid.http
   :code:

.. http:example:: tutorial/register-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: tutorial/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/upload-bid-proposal.http
   :code:

Спробуємо знову підтвердити пропозицію:

.. http:example:: tutorial/activate-bidder.http
   :code:

Учасник має завантажувати тільки ЕЦП на цьому етапі процедури.

Можна перевірити завантажені документи:

.. http:example:: tutorial/bidder-documents.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: tutorial/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозиціію, буде вимагатися новий підпиис:

.. http:example:: tutorial/activate-bidder-without-sign.http
   :code:

Пакетний режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~

У пакетному режимі (batch-mode) є можливість зареєструвати пропозицію одним запитом:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Аукціон
-------

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: tutorial/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: tutorial/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників:

.. http:example:: tutorial/bidder2-participation-url.http
   :code:

Список awards
-------------

Cписок аwards в статусі `pending` можна отримати за запитом:

.. http:example:: tutorial/awards-get.http
   :code:

Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `qualified: True` - при переході award з `pending` в `active`

* `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` учасника:

.. http:example:: tutorial/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` учасника:

.. http:example:: tutorial/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: tutorial/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: tutorial/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису має тип документу `documentType: notice` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/award-add-notice-document.http
   :code:

Спробуємо дискваліфікувати award, перевівши його зі статусу `pending` в `unsuccessful`.

.. http:example:: tutorial/award-qualification-unsuccessful.http
   :code:

Бачимо, що це неможливо. Замовник спочатку має активувати award в статусі `pending`, а потім перевести його в статус `cancelled`.

.. http:example:: tutorial/award-qualification-active.http
   :code:

Скасовуємо активний award.

.. http:example:: tutorial/award-qualification-cancelled.http
   :code:

Бачимо, що згенеровано новий award в статусі `pending` для того ж Учасника. Тепер Замовник може успішно перевести award з статусу  `pending` в `unsuccessful`.

.. http:example:: tutorial/award-qualification-unsuccessful1.http
   :code:

Кваліфікаційна комісія реєструє своє рішення через такий виклик:

.. http:example:: tutorial/confirm-qualification.http
   :code:

Замовник має заповнити інформацію про продовження терміну дії Учасника в полі `description`.


.. index:: Налаштування угоди

Налаштування угоди
------------------

В режимі Е-Контрактінгу угода створюється безпосередньо в системі угод.

.. note::
    Деякі дані для забезпечення сумісності будуть дублюватись в закупівлі до тих пір, поки угода не буде активована.

Більше дізнатись про роботу з Е-Контрактінгом в системі угод можна в розділі :ref:`contracting_tutorial`.


Скасування закупівлі
--------------------

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у статусі `active.auction` чи у кінцевому стані, наприклад, `usuccesfull`, `canceled`, `complete`).

Для цього потрібно виконати наступні кроки:

1. Приготуйте запит на скасування
2. Наповніть його протоколом про причини скасування
3. Скасуйте закупівлю через подані причини.

Запит на скасування, який не пройшов активації (3-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Див. структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

При скасуванні, замовник має визначити один з чотирьох типів reasonType: `noDemand`, `unFixable`, `forceMajeure` aбо `expensesCut`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`.

.. http:example:: tutorial/prepare-cancellation.http
   :code:


Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скарги.

Завантаження вмісту файлу

.. http:example:: tutorial/upload-cancellation-doc.http
   :code:

Зміна опису документа та інших властивостей

.. http:example:: tutorial/patch-cancellation.http
   :code:

Завантаження нової версії документа

.. http:example:: tutorial/update-cancellation-doc.http
   :code:

Активація запиту та скасування закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: tutorial/active-cancellation.http
   :code:


Можливо, буде корисно побачити актуальні вимоги: `Сценарії ручного тестування для III рівня акредитації <https://docs.google.com/spreadsheets/d/1-AT2RjbnSFAP75x6YNDvhKeN2Cy3tMlG6kb0tt6FScs/edit#gid=0>`_ і `Сценарії ручного тестування для IV рівня акредитації <https://docs.google.com/spreadsheets/d/1-93kcQ2EeuUU08aqPMDwMeAjnG2SGnEEh5RtjHWOlOY/edit#gid=0>`_.
