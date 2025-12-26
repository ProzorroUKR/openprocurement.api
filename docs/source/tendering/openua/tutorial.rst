.. _openua_tutorial:

Туторіал
========

.. index:: Tender

Конфігурація
------------

Набір можливих значень конфігурації:

.. csv-table::
   :file: csv/config.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Набір можливих значень `procuringEntity.kind` для `aboveThresholdUA`
--------------------------------------------------------------------

.. csv-table::
   :file: csv/kind.csv
   :header-rows: 1

Створення закупівлі
-------------------

Введемо data атрибут у поданому тілі:

.. http:example:: http/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `draft`.

Особливість відкритих торгів в тому, що ``procurementMethodType`` було змінено з ``belowThreshold`` на ``aboveThresholdUA``.  Також тут неможливо встановити ``enquiryPeriod``, бо він буде призначений автоматично.

Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: http/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Подивимось, що показує список закупівель:

.. http:example:: http/tender-listing-no-auth.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу `active.tendering`

Закупівля може складатись із декількох лотів. Можна створити лот таким чином:

.. http:example:: http/tender-add-lot.http
   :code:

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: http/tender-add-relatedLot-to-item.http
   :code:

Активація закупівлі
-------------------

Спочатку нам потрібно додати вийняткові критерії до нашої закупівлі(:ref:`Про критерії ви можете дізнатися тут<criteria_operation>`)

.. http:example:: http/add-exclusion-criteria.http
   :code:

Перед активацією тендера необхідно обов'язково додати файл підпису. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/add-notice-document.http
   :code:

Після додавання необхідних критеріїв та файлу підпису ми можемо активувати закупівлю:

.. http:example:: http/tender-activating.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: http/active-tender-listing-no-auth.http
   :code:

Ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату.

Редагування закупівлі
---------------------

Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: http/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: http/tender-listing-after-patch.http
   :code:


Замовник не може редагувати закупівлю, якщо залишилось менше 7 днів до завершення періоду подання пропозицій. API таких змін не прийме.

.. http:example:: http/update-tender-after-enqiery.http
   :code:

Ось чому потрібно продовжити період подання пропозицій на 7 днів.

.. http:example:: http/update-tender-after-enqiery-with-update-periods.http
   :code:

Замовник може встановити забезпечення тендерної пропозиції:

.. http:example:: http/set-bid-guarantee.http
   :code:


.. index:: Document

Завантаження документів
-----------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: http/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції `документів`, щоб підтвердити дію:

.. http:example:: http/tender-documents.http
   :code:

Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: http/upload-award-criteria.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: http/tender-documents-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: http/update-award-criteria.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: http/tender-documents-3.http
   :code:


.. index:: Звернення, Question, Answer

Звернення
---------

Якщо закупівля має статус ``active.tendering`` та дата завершення періоду подання пропозицій ``Tender.enqueryPeriod.endDate`` ще не прийшла , то зацікавлені учасники можуть подавати звернення чи просити уточнень умов закупівлі:

.. http:example:: http/ask-question.http
   :code:

Замовник може відповісти на них:

.. http:example:: http/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: http/list-question.http
   :code:

або окрему відповідь:

.. http:example:: http/get-answer.http
   :code:


Звернення можна задавати лише протягом періоду уточнень ``Tender.enqueryPeriod``

.. http:example:: http/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Реєстрація пропозиції
---------------------

Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.

Учасник може зареєструвати пропозицію для лоту №1 зі статусом ``draft`` (чернетка):

.. http:example:: http/register-bidder.http
   :code:

Та додамо відповіді на вимоги критеріїв:

.. http:example:: http/add-requirement-responses-to-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: http/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: http/upload-bid-proposal.http
   :code:

Спробуємо підтвердити пропозицію:

.. http:example:: http/activate-bidder.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: http/bidder-documents.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: http/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозиціію, буде вимагатися новий підпиис:

.. http:example:: http/activate-bidder-without-sign.http
   :code:

Пропозиція стає недійсною
~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі:

.. http:example:: http/bidder-after-changing-tender.http
   :code:

Підтвердження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~~

Учасник повинен підтвердити свою пропозицію:

.. http:example:: http/bidder-activate-after-changing-tender.http
   :code:

Для того, щоб процедура відкритих торгів відбулась, необхідно хоча б два учасника, тобто хоча б дві пропозиції повинні бути зареєстровані до початку аукціону:

.. http:example:: http/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Аукціон
-------

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: http/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: http/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників:

.. http:example:: http/bidder2-participation-url.http
   :code:


Аномально низька ціна
---------------------

Об’єкт award може містити milestone типу ``apl`` 

.. http:example:: http/get-awards-list.http
   :code:


Замовник не може змінити статус award до настання “milestone.dueDate”

.. http:example:: http/fail-disqualification.http
   :code:


Протягом цього часу учасник торгів може завантажувати документи ``evidence`` до своєї заявки

.. http:example:: http/post-evidence-document.http
   :code:



Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `eligible: True` та `qualified: True` - при переході award з `pending` в `active`

* `eligible: False` та `qualified: True` АБО `eligible: True` та `qualified: False` АБО `eligible: False` та `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` та `eligible` учасника:

.. http:example:: http/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` або `non-eligible` учасника:

.. http:example:: http/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: http/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/award-add-notice-document.http
   :code:

Кваліфікаційна комісія реєструє своє рішення:

.. http:example:: http/confirm-qualification.http
   :code:


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

1. Приготуйте запит на скасування.
2. Наповніть його протоколом про причини скасування.
3. Проходження періоду оскарження(триває 10 днів)
4. Скасуйте закупівлю через подані причини.

Запит на скасування, який не пройшов активації (4-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Для відміни скасування закупівлі, вам потрібно оновоить статус скасування до `unsuccessful` з `draft` чи `pending`.

Дивіться структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

При скасуванні, замовник має визначити один з чотирьох типів reasonType: `noDemand`, `unFixable`, `forceMajeure` aбо `expensesCut`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`.

.. http:example:: http/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище.

.. http:example:: http/update-cancellation-reasonType.http
     :code:

Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скарги.

Завантажити вміст файлу

.. http:example:: http/upload-cancellation-doc.http
   :code:

Зміна опису документа та інших властивостей


.. http:example:: http/patch-cancellation.http
   :code:

Завантажити нову версію документа


.. http:example:: http/update-cancellation-doc.http
   :code:

Проходження періоду оскарження
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для того щоб перейти до періоду оскарження потрібно змінити стаутс скасування з `draft` на `pending`.

.. http:example:: http/pending-cancellation.http
   :code:

Коли скасування закупівлі в статусі `pending` замовнику зобороняються всі дії по закупівлі.

Активація запиту та скасування закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

якщо період оскарження(триває 10 днів) скінчився та не було ніяких скарг на скасування закупівлі або скарги були скасовані, то скасування автоматично зміює статус на `active`.
