.. _simpleAsset_tutorial:

Простий актив - ``simpleAsset.arma``
====================================

.. index:: Tender

Відбір управителя простого активу відрізняється від :ref:`complexAsset_tutorial` тим, що в ньому немає прекваліфікації. Коло учасників визначається заздалегідь — рамковою угодою АРМА, на яку посилається закупівля. Після завершення періоду подання пропозицій закупівля одразу переходить до аукціону.

Конфігурація
------------

Набір можливих значень конфігурації:

.. csv-table::
   :file: simpleAsset/csv/config.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Дозволені значення `procuringEntity.kind`
-----------------------------------------

.. csv-table::
   :file: simpleAsset/csv/kind.csv
   :header-rows: 1

.. index:: Agreement

Угода попереднього відбору
--------------------------

Закупівля простого активу проводиться серед учасників, які пройшли відбір за рамковою угодою з ``frameworkType: assetRecoveryManagementAgency``. Угода створюється автоматично після активації першої кваліфікації у відборі, детальніше — в туторіалі :ref:`framework_arma_tutorial`.

Подивимось на угоду, яку будемо використовувати:

.. http:example:: simpleAsset/http/tutorial/view-agreement.http
   :code:

Посилання на угоду передається в полі `agreement` і є обов'язковим. Без нього закупівлю створити не вдасться:

.. http:example:: simpleAsset/http/tutorial/tender-post-attempt-without-agreement.http
   :code:

Угода, якої не існує, теж не приймається:

.. http:example:: simpleAsset/http/tutorial/tender-post-attempt-unknown-agreement.http
   :code:

Додатково, під час активації закупівлі перевіряється, що:

* угода має тип ``assetRecoveryManagementAgency``;
* `agreement.procuringEntity.identifier` збігається з `tender.procuringEntity.identifier`;
* угода у статусі `active`;
* в угоді є щонайменше 2 активні контракти.

Створення закупівлі
-------------------

Введемо data атрибут у поданому тілі:

.. http:example:: simpleAsset/http/tutorial/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `draft`.

Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: simpleAsset/http/tutorial/blank-tender-view.http
   :code:

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Подивимось, що показує список закупівель:

.. http:example:: simpleAsset/http/tutorial/tender-listing-no-auth.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу `active.tendering`

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: simpleAsset/http/tutorial/tender-add-relatedLot-to-item.http
   :code:

Активація закупівлі
-------------------

Перед активацією тендера необхідно обов'язково додати файл підпису. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: simpleAsset/http/tutorial/notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: simpleAsset/http/tutorial/add-notice-document.http
   :code:

Після додавання файлу підпису ми можемо активувати закупівлю:

.. http:example:: simpleAsset/http/tutorial/tender-activating.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: simpleAsset/http/tutorial/active-tender-listing-no-auth.http
   :code:

Ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату.

Редагування закупівлі
---------------------

Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: simpleAsset/http/tutorial/patch-items-value-periods.http
   :code:

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: simpleAsset/http/tutorial/tender-listing-after-patch.http
   :code:

.. index:: Document

Завантаження документів
-----------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: simpleAsset/http/tutorial/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів (`documents`), щоб підтвердити дію:

.. http:example:: simpleAsset/http/tutorial/tender-documents.http
   :code:

Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: simpleAsset/http/tutorial/upload-award-criteria.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: simpleAsset/http/tutorial/tender-documents-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: simpleAsset/http/tutorial/update-award-criteria.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: simpleAsset/http/tutorial/tender-documents-3.http
   :code:

Продовження періоду подання пропозицій
--------------------------------------

Замовник не може редагувати закупівлю, якщо залишилось менше 7 днів до завершення періоду подання пропозицій. API таких змін не прийме.

.. http:example:: simpleAsset/http/tutorial/update-tender-before-tendering-end.http
   :code:

Ось чому потрібно продовжити період подання пропозицій (`tenderPeriod`) на 7 днів.

.. http:example:: simpleAsset/http/tutorial/update-tender-with-extended-period.http
   :code:

.. index:: Bidding

Реєстрація пропозиції
---------------------

Реєстрація пропозиції
~~~~~~~~~~~~~~~~~~~~~

Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.

Учасник може зареєструвати ставку для лоту №1 із статусом ``draft`` (чернетка):

.. http:example:: simpleAsset/http/tutorial/register-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: simpleAsset/http/tutorial/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: simpleAsset/http/tutorial/upload-bid-proposal.http
   :code:

Спробуємо підтвердити пропозицію:

.. http:example:: simpleAsset/http/tutorial/activate-bidder.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: simpleAsset/http/tutorial/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозицію, буде вимагатися новий підпис:

.. http:example:: simpleAsset/http/tutorial/activate-bidder-without-sign.http
   :code:

Конфіденційність
~~~~~~~~~~~~~~~~

Завантажимо документ:

.. http:example:: simpleAsset/http/tutorial/upload-bid-private-proposal.http
   :code:

Щоб зробити документ "приватним", потрібно встановити поля `confidentiality` та `confidentialityRationale`.

Значенням поля `confidentiality` може бути або `buyerOnly` - документ приватний, або `public` - документ публічно доступний.

Вміст приватних документів (`buyerOnly`) закритий для всіх крім замовника і учасника, який подав ці документи.

Поле `confidentialityRationale` необхідне лише для приватних документів. Його значенням має бути пояснення причини конфіденційності документа (не менше ніж 30 символів).

Позначимо документ як "приватний":

.. http:example:: simpleAsset/http/tutorial/mark-bid-doc-private.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: simpleAsset/http/tutorial/bidder-documents.http
   :code:

.. _simpleAsset_envelopes:

Завантаження документів, що підтверджують відповідність, фінансових та кваліфікаційних документів
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Документи, що підтверджують відповідність, фінансові та кваліфікаційні документи також є частиною пропозиції, але зберігаються в різних точках входу.

Для того, щоб створити і/або отримати фінансові документи потрібно використати точку входу ``financial_documents``:

.. http:example:: simpleAsset/http/tutorial/upload-bid-financial-document-proposal.http
   :code:

Отримати фінансові документи:

.. http:example:: simpleAsset/http/tutorial/bidder-financial-documents.http
   :code:

Для того, щоб створити і/або отримати документи, що підтверджують відповідність потрібно використати точку входу ``eligibility_documents``:

.. http:example:: simpleAsset/http/tutorial/upload-bid-eligibility-document-proposal.http
   :code:

Для того, щоб створити і/або отримати документи, що підтверджують кваліфікацію, потрібно використати точку входу ``qualification_documents``:

.. http:example:: simpleAsset/http/tutorial/upload-bid-qualification-document-proposal.http
   :code:

`Фінансові` та `кваліфікаційні` документи будуть публічно доступні після аукціону.

Пропозиція учасника зі всіма документами.

.. http:example:: simpleAsset/http/tutorial/bidder-view-financial-documents.http
   :code:

Зверніть увагу, що документи, що підтверджують відповідність, фінансові та кваліфікаційні документи зберігаються у `eligibilityDocuments`, `financialDocuments` та  `qualificationDocuments` атрибутах :ref:`Bid` відповідно.

Пропозиція стає недійсною
~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі:

.. http:example:: simpleAsset/http/tutorial/bidder-after-changing-tender.http
   :code:

Підтвердження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~~

Учасник повинен підтвердити свою пропозицію:

.. http:example:: simpleAsset/http/tutorial/bidder-activate-after-changing-tender.http
   :code:

Для того, щоб процедура відбулась, необхідно хоча б два учасника, тобто хоча б дві пропозиції повинні бути зареєстровані до початку аукціону:

.. http:example:: simpleAsset/http/tutorial/register-2nd-bidder.http
   :code:

Пакетний режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~

У пакетному режимі (batch-mode) є можливість зареєструвати пропозицію одним запитом. Зареєструйте ще одну пропозицію:

.. http:example:: simpleAsset/http/tutorial/register-3rd-bidder.http
   :code:

Аукціон
-------

Прекваліфікації в цьому типі закупівель немає, тому після завершення ``tenderPeriod`` закупівля одразу переходить у статус ``active.auction``, і всі підтверджені пропозиції потрапляють до аукціону.

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: simpleAsset/http/tutorial/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: simpleAsset/http/tutorial/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників:

.. http:example:: simpleAsset/http/tutorial/bidder2-participation-url.http
   :code:

.. index:: Awarding, Qualification

Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `eligible: True` та `qualified: True` - при переході award з `pending` в `active`

* `eligible: False` та `qualified: True` АБО `eligible: True` та `qualified: False` АБО `eligible: False` та `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` та `eligible` учасника:

.. http:example:: simpleAsset/http/tutorial/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` або `non-eligible` учасника:

.. http:example:: simpleAsset/http/tutorial/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: simpleAsset/http/tutorial/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: simpleAsset/http/tutorial/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: simpleAsset/http/tutorial/award-add-notice-document.http
   :code:

Кваліфікаційна комісія реєструє своє рішення:

.. http:example:: simpleAsset/http/tutorial/confirm-qualification.http
   :code:

.. index:: Налаштування угоди

Налаштування угоди
------------------

Е-Контрактінг недоступний для цього типу закупівель.

В режимі звичайного контрактінгу угода буде створена спочатку в системі закупівель.

Замовник може вказати відсоток, на який домовились сторони:

.. http:example:: simpleAsset/http/tutorial/contract-set-contract-value-percentage.http
   :code:

Скасування закупівлі
--------------------

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у статусі `active.auction` чи у кінцевому стані, наприклад, `unsuccessful`, `canceled`, `complete`).

Для цього потрібно виконати наступні кроки:

1. Приготуйте запит на скасування.
2. Наповніть його протоколом про причини скасування.
3. Скасуйте закупівлю через подані причини.

Запит на скасування, який не пройшов активації (3-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Для відміни скасування закупівлі, вам потрібно оновити статус скасування до `unsuccessful` з `draft` чи `pending`

Дивіться структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

При скасуванні, замовник має визначити один з п'яти типів reasonType: `noDemand`, `unFixable`, `forceMajeure`, `expensesCut` або `noLocalization`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`.

.. http:example:: simpleAsset/http/tutorial/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище.

.. http:example:: simpleAsset/http/tutorial/update-cancellation-reasonType.http
   :code:

Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Завантажте вміст файлу

.. http:example:: simpleAsset/http/tutorial/upload-cancellation-doc.http
   :code:

Змініть опис документа та інші властивості

.. http:example:: simpleAsset/http/tutorial/patch-cancellation.http
   :code:

Завантажте нову версію документа

.. http:example:: simpleAsset/http/tutorial/update-cancellation-doc.http
   :code:

Скасування
~~~~~~~~~~

Через відсутність періодів оскарження в цьому типі закупівлі скасування одразу будуть переходити в статус `active`.

Перед активацією запиту на скасування закупівлі необхідно додати файл підпису до `cancellation`. Якщо нема файлу підпису під час активації скасування, ми побачимо помилку:

.. http:example:: simpleAsset/http/tutorial/cancellation-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: cancellationReport` та `title: *.p7s`. Додамо такий документ:

.. http:example:: simpleAsset/http/tutorial/upload-cancellation-report-doc.http
   :code:

Змінимо статус скасування з `draft` на `pending`:

.. http:example:: simpleAsset/http/tutorial/pending-cancellation.http
   :code:

Скасування автоматично буде в статусі `active`, через відсутність періодів оскарження.

Закупівля теж змінить свій статус на `cancelled`, замовнику забороняються всі дії по закупівлі.
