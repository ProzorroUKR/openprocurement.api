.. _tutorial_stage2EU:

Конфігурація
------------

Набір можливих значень конфігурації:

.. csv-table::
   :file: csv/config-eu-stage2.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Дозволені значення `procuringEntity.kind`
-----------------------------------------

.. csv-table::
   :file: csv/kind-eu-stage2.csv
   :header-rows: 1

Редагування закупівлі
---------------------

На першому етапі поле ``procurementMethodType`` було встановлено  ``CompetitiveDialogueEU`` тому на другому етапі процедура схожа на Open EU

На другому етапі є можливість редагувати тільки ``tenderPeriod.endDate`` та ``deliveryDate`` в ``items``.

Якщо спробувати відредагувати якесь заборонене поле, то побачимо помилку:

.. http:example:: tutorial/stage2/EU/patch-tender-invalid.http
   :code:

Спробуємо внести дозволені зміни:

.. http:example:: tutorial/stage2/EU/patch-tender-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Потрібно перевести тендер в статус ``active.tendering``, щоб мати змогу створювати пропозиції.

.. http:example:: tutorial/stage2/EU/tender-activate.http
   :code:


Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: tutorial/stage2/EU/tender-listing-after-patch.http
   :code:

Замовник не може редагувати закупівлю, якщо залишилось менше 7 днів до завершення періоду подання пропозицій. API таких змін не прийме.

.. http:example:: tutorial/stage2/EU/update-tender-after-enqiery.http
   :code:

Ось чому потрібно продовжити період подання пропозицій (`tenderPeriod`) на 7 днів.

.. http:example:: tutorial/stage2/EU/update-tender-after-enqiery-with-update-periods.http
   :code:

.. index:: Document

Завантаження документів
-----------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: tutorial/stage2/EU/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів (`documents`), щоб підтвердити дію:

.. http:example:: tutorial/stage2/EU/tender-documents.http
   :code:

Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: tutorial/stage2/EU/upload-award-criteria.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: tutorial/stage2/EU/tender-documents-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: tutorial/stage2/EU/update-award-criteria.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: tutorial/stage2/EU/tender-documents-3.http
   :code:


.. index:: Уточнення і звернення, Question, Answer

Уточнення і звернення
---------------------

Якщо закупівля має статус ``active.tendering`` та дата завершення періоду подання пропозицій ``Tender.enquiryPeriod.endDate`` ще не прийшла , то зацікавлені учасники можуть подавати звернення чи просити уточнень умов закупівлі. Звернення можуть задавати тільки учасники, які були допущені на першому етапі, інші при спробі отримають помилку.

.. http:example:: tutorial/stage2/EU/ask-question-bad-participant.http
   :code:

Учасник з першого етапу подасть звернення.

.. http:example:: tutorial/stage2/EU/ask-question.http
   :code:

Замовник може відповісти на них:

.. http:example:: tutorial/stage2/EU/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: tutorial/stage2/EU/list-question.http
   :code:

або окрему відповідь:

.. http:example:: tutorial/stage2/EU/get-answer.http
   :code:


Звернення можна задавати лише протягом періоду уточнень ``Tender.enquiryPeriod``.

.. http:example:: tutorial/stage2/EU/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Реєстрація пропозиції
---------------------

Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.Пропозицію можливо створити зі статусом `draft`

Як і зі зверненнями, тільки учасник який був допущений на першому етапі може реєструвати попозиції на другогому.В іншому випадку буде повернена помилка.

.. http:example:: tutorial/stage2/EU/try-register-bidder.http
   :code:

Отримали помилку, теперь учасник який був допущений на першому етапі

.. http:example:: tutorial/stage2/EU/register-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: tutorial/stage2/EU/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/stage2/EU/upload-bid-proposal.http
   :code:

Спробуємо підтвердити пропозицію:

.. http:example:: tutorial/stage2/EU/activate-bidder.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: tutorial/stage2/EU/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозицію, буде вимагатися новий підпис:

.. http:example:: tutorial/stage2/EU/activate-bidder-without-sign.http
   :code:

Конфіденційність
^^^^^^^^^^^^^^^^

Документи можуть бути або публічними, або приватними:

  1. Приватність документа можна змінити тільки для останньої версії.
  2. При завантаженні нової версії, налаштування приватності копіюються з попередньої версії документа.
  3. Налаштування приватності можна міняти тільки під час періоду подання пропозицій (зі статусом `active.tendering`).
  4. Якщо закупівля має статус `active.qualification`, переможець може завантажувати тільки публічні документи.

Завантажимо приватний документ:

.. http:example:: tutorial/stage2/EU/upload-bid-private-proposal.http
   :code:

Щоб зробити документ "приватним", потрібно встановити поля `confidentiality` та `confidentialityRationale`.

Значенням поля `confidentiality` може бути або `buyerOnly` - документ приватний, або `public` - документ публічно доступний.

Вміст приватних документів (`buyerOnly`) закритий для всіх крім замовника і учасника, який подав ці документи.

Поле `confidentialityRationale` необхідне лише для приватних документів. Його значенням має бути пояснення причини конфіденційності документа (не менше ніж 30 символів).

Позначимо документ як "приватний":

.. http:example:: tutorial/stage2/EU/mark-bid-doc-private.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: tutorial/stage2/EU/bidder-documents.http
   :code:

.. _stage2EU_envelopes:

Завантаження документів, що підтверджують відповідність, фінансових документів.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Документи, що підтверджують відповідність, фінансові документи також є частиною пропозиції, але зберігаються в різних точках входу.

Для того, щоб створити і/або отримати фінансові документи потрібно використати точку входу ``financial_documents``:

.. http:example:: tutorial/stage2/EU/upload-bid-financial-document-proposal.http
   :code:

Отримати фінансові документи:

.. http:example:: tutorial/stage2/EU/bidder-financial-documents.http
   :code:


`Фінансові` документи будуть публічно доступні після аукціону. Документи, `що підтверджують відповідність`, будуть публічно доступні на етапі прекваліфікації.

Пропозиція учасника зі всіма документами:

.. http:example:: tutorial/stage2/EU/bidder-view-financial-documents.http
   :code:

Зверніть увагу, що документи, що підтверджують відповідність, фінансові документи зберігаються у `financialDocuments` атрибутах :ref:`Bid` відповідно.


Пропозиція стає недійсною
^^^^^^^^^^^^^^^^^^^^^^^^^

Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі:

.. http:example:: tutorial/stage2/EU/bidder-after-changing-tender.http
   :code:

Підтвердження пропозиції
^^^^^^^^^^^^^^^^^^^^^^^^

Учасник повинен підтвердити свою пропозицію:

.. http:example:: tutorial/stage2/EU/bidder-activate-after-changing-tender.http
   :code:

Для того, щоб другий етап процедуру конкурентного діалогу  відбувся, необхідно хоча б два учасника, тобто хоча б дві пропозиції повинні бути зареєстровані до початку аукціону:

.. http:example:: tutorial/stage2/EU/register-2nd-bidder.http
   :code:

Пакетний режим реєстрації
^^^^^^^^^^^^^^^^^^^^^^^^^

У пакетному режимі (batch-mode) є можливість зареєструвати пропозицію одним запитом. Зареєструйте ще одну пропозицію:

.. http:example:: tutorial/stage2/EU/register-3rd-bidder.http
   :code:


.. index:: Awarding, Qualification

Кваліфікація пропозицій
-----------------------

Для другого етапу конкурентної процедури необхідна кваліфікація пропозицій.

Переглянемо список кваліфікацій:


.. http:example:: tutorial/stage2/EU/qualifications-listing.http
   :code:

Підтвердіть перші дві пропозиції через кваліфікаційні об’єкти:

.. http:example:: tutorial/stage2/EU/approve-qualification1.http
   :code:

.. http:example:: tutorial/stage2/EU/approve-qualification2.http
   :code:

Можна відхилити пропозицію:

.. http:example:: tutorial/stage2/EU/reject-qualification3.http
   :code:

Та перевірити, що вже кваліфіковані пропозиції переключені в стан `active`:

.. http:example:: tutorial/stage2/EU/qualificated-bids-view.http
   :code:

Відхилена пропозиція не присутня в списку `bids/`.

Можна отримати доступ до відхиленої пропозиції за її ідентифікатором `id`:

.. http:example:: tutorial/stage2/EU/rejected-bid-view.http
   :code:

Замовник підтверджує кваліфікацію переходом до наступного статусу.

Перед схваленням рішення необхідно додати файл підпису до тендеру. Файл підпису повинен бути доданий до тендеру загалом. Якщо нема файлу підпису під час схвалення кваліфікації, ми побачимо помилку:

.. http:example:: tutorial/stage2/EU/pre-qualification-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: evaluationReports` та `title: *.p7s`. Додамо такий документ:

.. http:example:: tutorial/stage2/EU/upload-evaluation-reports-doc.http
   :code:

Ще раз схвалимо кваліфікацію заявок:

.. http:example:: tutorial/stage2/EU/pre-qualification-confirmation.http
   :code:

Зверніть увагу на період блокування в 10 днів під час `qualificationPeriod`.

Аукціон
-------

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: tutorial/stage2/EU/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: tutorial/stage2/EU/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників.

.. http:example:: tutorial/stage2/EU/bidder2-participation-url.http
   :code:

Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `eligible: True` та `qualified: True` - при переході award з `pending` в `active`

* `eligible: False` та `qualified: True` АБО `eligible: True` та `qualified: False` АБО `eligible: False` та `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` та `eligible` учасника:

.. http:example:: tutorial/stage2/EU/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` або `non-eligible` учасника:

.. http:example:: tutorial/stage2/EU/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: tutorial/stage2/EU/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: tutorial/stage2/EU/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису має тип документу `documentType: notice` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/stage2/EU/award-add-notice-document.http
   :code:

Кваліфікаційна комісія реєструє своє рішення:

.. http:example:: tutorial/stage2/EU/confirm-qualification.http
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

Для відміни скасування закупівлі, вам потрібно оновити статус скасування до `unsuccessful` з `draft` чи `pending`

Дивіться структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у статусі `active.auction` чи у кінцевому стані, наприклад, `unsuccessful`, `canceled`, `complete`).

Для цього потрібно виконати наступні кроки:

При скасуванні, замовник має визначити один з чотирьох типів reasonType: `noDemand`, `unFixable`, `forceMajeure` aбо `expensesCut`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`:

.. http:example:: tutorial/stage2/EU/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище

.. http:example:: tutorial/stage2/EU/update-cancellation-reasonType.http
   :code:

Наповнення протоколом та іншою супровідною документацією
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Цей крок обов'язковий. Без документів ви не можете оновити статус скарги.

Завантажте вміст файлу

.. http:example:: tutorial/stage2/EU/upload-cancellation-doc.http
   :code:

Змініть опис документа та інші властивості


.. http:example:: tutorial/stage2/EU/patch-cancellation.http
   :code:

Завантажте нову версію документа


.. http:example:: tutorial/stage2/EU/update-cancellation-doc.http
   :code:

Проходження періоду оскарження
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Для того щоб перейти до періоду оскарження потрібно змінити статус скасування з `draft` на `pending`.

Перед активацією запиту на скасування закупівлі необхідно додати файл підпису до `cancellation`. Якщо нема файлу підпису під час активації скасування, ми побачимо помилку:

.. http:example:: tutorial/stage2/EU/cancellation-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: cancellationReport` та `title: *.p7s`. Додамо такий документ:

.. http:example:: tutorial/stage2/EU/upload-cancellation-report-doc.http
   :code:

Змінимо статус скасування з `draft` на `pending`:

.. http:example:: tutorial/stage2/EU/pending-cancellation.http
   :code:

Коли скасування закупівлі в статусі `pending` замовнику забороняються всі дії по закупівлі.

Активація запиту та скасування закупівлі
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Якщо період оскарження(триває 10 днів) скінчився та не було ніяких скарг на скасування закупівлі або скарги були скасовані, то скасування автоматично змінює статус на `active`

.. http:example:: tutorial/stage2/EU/active-cancellation.http
   :code:
