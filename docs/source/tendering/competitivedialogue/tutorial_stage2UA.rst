.. _tutorial_stage2UA:

Конфігурація
------------

Набір можливих значень конфігурації:

.. csv-table::
   :file: csv/config-ua-stage2.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Набір можливих значень `procuringEntity.kind` для `competitiveDialogueUA.stage2`
--------------------------------------------------------------------------------

.. csv-table::
   :file: csv/kind-ua-stage2.csv
   :header-rows: 1

Редагування закупівлі
---------------------

На першому етапі параметр ``procurementMethodType`` був ``CompetitiveDialogueUA`` тому на другому етапі створюється процедура, яка схожа на Open UA процедуру.

На другому етапі є можливість редагувати тільки ``tenderPeriod.endDate`` та ``deliveryDate`` в ``items``.

Якщо спробувати відредагувати якесь заборонене поле, то побачимо помилку:

.. http:example:: tutorial/stage2/UA/patch-tender-invalid.http
   :code:

Спробуємо внести дозволені зміни:

.. http:example:: tutorial/stage2/UA/patch-tender-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: tutorial/stage2/UA/tender-listing-after-patch.http
   :code:


Замовник не може редагувати закупівлю, якщо залишилось менше 7 днів до завершення періоду подання пропозицій. API таких змін не прийме.

.. http:example:: tutorial/stage2/UA/update-tender-after-enqiery.http
   :code:

Ось чому потрібно продовжити період подання пропозицій на 7 днів.

.. http:example:: tutorial/stage2/UA/update-tender-after-enqiery-with-update-periods.http
   :code:


.. index:: Document

Завантаження документів
-----------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: tutorial/stage2/UA/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції `документів`, щоб підтвердити дію:

.. http:example:: tutorial/stage2/UA/tender-documents.http
   :code:

Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: tutorial/stage2/UA/upload-award-criteria.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: tutorial/stage2/UA/tender-documents-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: tutorial/stage2/UA/update-award-criteria.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: tutorial/stage2/UA/tender-documents-3.http
   :code:


.. index:: Звернення, Question, Answer

Звернення
---------

Якщо закупівля має статус ``active.tendering`` та дата завершення періоду подання пропозицій ``Tender.enqueryPeriod.endDate`` ще не прийшла , то зацікавлені учасники можуть подавати звернення чи просити уточнень умов закупівлі. Звернення можуть задавати тільки учасники, які були допущені на першому етапі, інші при спробі отримають помилку:

.. http:example:: tutorial/stage2/UA/ask-question-bad-participant.http
   :code:


.. http:example:: tutorial/stage2/UA/ask-question.http
   :code:

Замовник може відповісти на них:

.. http:example:: tutorial/stage2/UA/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: tutorial/stage2/UA/list-question.http
   :code:

або окрему відповідь:

.. http:example:: tutorial/stage2/UA/get-answer.http
   :code:


Звернення можна задавати лише протягом періоду уточнень ``Tender.enqueryPeriod``.

.. http:example:: tutorial/stage2/UA/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Реєстрація пропозиції
---------------------

Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.

Як і зі зверненнями тільки допущені учасники на першому етапі можуть реєструвати пропозиції. Якщо учасник якого не було допущено на першому етапі пробує створити пропозицію то йому поверне помилку.

.. http:example:: tutorial/stage2/UA/try-register-bidder.http
   :code:

Учасник може зареєструвати цінову пропозицію:

.. http:example:: tutorial/stage2/UA/register-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: tutorial/stage2/UA/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/stage2/UA/upload-bid-proposal.http
   :code:

Спробуємо знову підтвердити пропозицію:

.. http:example:: tutorial/stage2/UA/activate-bidder.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: tutorial/stage2/UA/bidder-documents.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: tutorial/stage2/UA/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозиціію, буде вимагатися новий підпиис:

.. http:example:: tutorial/stage2/UA/activate-bidder-without-sign.http
   :code:

Пропозиція стає недійсною
~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі:

.. http:example:: tutorial/stage2/UA/bidder-after-changing-tender.http
   :code:

Підтвердження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~~

Учасник повинен підтвердити свою пропозицію:

.. http:example:: tutorial/stage2/UA/bidder-activate-after-changing-tender.http
   :code:


Для того, щоб другий етап процедуру конкурентного діалогу відбувся, необхідно хоча б два учасника, тобто хоча б дві пропозиції повинні бути зареєстровані до початку аукціону.

Пакетний режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~

У пакетному режимі (batch-mode) є можливість зареєструвати пропозицію одним запитом. Зареєструйте ще одну пропозицію:

.. http:example:: tutorial/stage2/UA/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Аукціон
-------

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: tutorial/stage2/UA/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: tutorial/stage2/UA/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників.

.. http:example:: tutorial/stage2/UA/bidder2-participation-url.http
   :code:

Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `eligible: True` та `qualified: True` - при переході award з `pending` в `active`

* `eligible: False` та `qualified: True` АБО `eligible: True` та `qualified: False` АБО `eligible: False` та `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` та `eligible` учасника:

.. http:example:: tutorial/stage2/UA/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` або `non-eligible` учасника:

.. http:example:: tutorial/stage2/UA/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: tutorial/stage2/UA/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: tutorial/stage2/UA/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису має тип документу `documentType: notice` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/stage2/UA/award-add-notice-document.http
   :code:

Кваліфікаційна комісія реєструє своє рішення:

.. http:example:: tutorial/stage2/UA/confirm-qualification.http
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

Замовник може скасувати закупівлю у будь-який момент. Для цього виконайте наступні кроки:

1. Приготуйте запит на скасування.
2. Наповніть його протоколом про причини скасування.
3. Проходження періоду оскарження(триває 10 днів)
4. Скасуйте закупівлю через подані причини.

Запит на скасування, який не пройшов активації (4-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Для відміни скасування закупівлі, вам потрібно оновоить статус скасування до `unsuccessful` з `draft` чи `pending`

Дивіться структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у статусі `active.auction` чи у кінцевому стані, наприклад, `usuccesfull`, `canceled`, `complete`).

Для цього потрібно виконати наступні кроки:

При скасуванні, замовник має визначити один з чотирьох типів reasonType: `noDemand`, `unFixable`, `forceMajeure` aбо `expensesCut`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`:

.. http:example:: tutorial/stage2/EU/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище

.. http:example:: tutorial/stage2/UA/update-cancellation-reasonType.http
   :code:

Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скарги.

Завантажте вміст файлу

.. http:example:: tutorial/stage2/UA/upload-cancellation-doc.http
   :code:

Змініть опис документа та інші властивості


.. http:example:: tutorial/stage2/UA/patch-cancellation.http
   :code:

Завантажте нову версію документа


.. http:example:: tutorial/stage2/UA/update-cancellation-doc.http
   :code:

Проходження періоду оскарження
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для того щоб перейти до періоду оскарження потрібно змінити стаутс скасування з `draft` на `pending`.

.. http:example:: tutorial/stage2/UA/pending-cancellation.http
   :code:

Коли скасування закупівлі в статусі `pending` замовнику зобороняються всі дії по закупівлі.

Активація запиту та скасування закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо період оскарження(триває 10 днів) скінчився та не було ніяких скарг на скасування закупівлі або скарги були скасовані, то скасування автоматично зміює статус на `active`

.. http:example:: tutorial/stage2/UA/active-cancellation.http
   :code:
