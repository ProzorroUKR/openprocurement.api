.. _competitivedialogue_tutorial:

Туторіал
========

.. index:: Tender

Конфігурація
------------

Набір можливих значень конфігурації для :`competitiveDialogueEU`

.. csv-table::
   :file: csv/config-eu-stage1.csv
   :header-rows: 1

Набір можливих значень конфігурації для :`competitiveDialogueUA`

.. csv-table::
   :file: csv/config-ua-stage1.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Набір можливих значень `procuringEntity.kind` для `competitiveDialogueEU`
-------------------------------------------------------------------------

.. csv-table::
   :file: csv/kind-eu-stage1.csv
   :header-rows: 1

Набір можливих значень `procuringEntity.kind` для `competitiveDialogueUA`
-------------------------------------------------------------------------

.. csv-table::
   :file: csv/kind-ua-stage1.csv
   :header-rows: 1

Створення закупівлі
-------------------

Введемо data атрибут у поданому тілі:

.. http:example:: tutorial/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `draft`.

Особливість процедури конкурентний діалог в тому, що ``procurementMethodType`` може бути ``CompetitiveDialogueEU`` або ``CompetitiveDialogueUA``.

Якщо ``procurementMethodType`` була встановленя на ``CompetitiveDialogueEU`` то на другому етапі будет створенапроцедура яка схожа на Open EU, а якщо ``CompetitiveDialogueUA`` тоді на Open UA

Також тут неможливо встановити ``enquiryPeriod``, бо він буде призначений автоматично.

Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Подивимось, що показує список закупівель:

.. http:example:: tutorial/tender-listing-no-auth.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу ``active.tendering``

Закупівля може складатись із декількох лотів. Можна створити лот таким чином:

.. http:example:: tutorial/tender-add-lot.http
   :code:

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: tutorial/tender-add-relatedLot-to-item.http
   :code:

Активація закупівлі
-------------------

Спочатку нам потрібно додати вийняткові критерії до нашої закупівлі(:ref:`Про критерії ви можете дізнатися тут<criteria_operation>`)

.. http:example:: tutorial/add-exclusion-criteria.http
   :code:

Після додавання необхідних критеріїв ми иожемо активувати закупівлю:

.. http:example:: tutorial/tender-activating.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: tutorial/active-tender-listing-no-auth.http
   :code:

Тепер ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату.


Редагування закупівлі
---------------------

Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: tutorial/tender-listing-after-patch.http
   :code:

Замовник не може редагувати закупівлю, якщо залишилось менше 7 днів до завершення періоду подання пропозицій. API таких змін не прийме.

.. http:example:: tutorial/update-tender-after-enqiery.http
   :code:

Ось чому потрібно продовжити період подання пропозицій (`tenderPeriod`) на 7 днів.

.. http:example:: tutorial/update-tender-after-enqiery-with-update-periods.http
   :code:

Замовник може встановити забезпечення тендерної пропозиції

.. http:example:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

Завантаження документів
-----------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: tutorial/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів (`documents`), щоб підтвердити дію:

.. http:example:: tutorial/tender-documents.http
   :code:


І знову можна перевірити, що є два завантажених документа.

.. http:example:: tutorial/tender-documents-2.http
   :code:


І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: tutorial/tender-documents-3.http
   :code:


.. index:: Уточнення і звернення, Question, Answer

Уточнення і звернення
---------------------

Якщо закупівля має статус ``active.tendering`` та дата завершення періоду подання пропозицій ``Tender.enqueryPeriod.endDate`` ще не прийшла , то зацікавлені учасники можуть подавати звернення чи просити уточнень умов закупівлі:

.. http:example:: tutorial/ask-question.http
   :code:

Замовник може відповісти на них:

.. http:example:: tutorial/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: tutorial/list-question.http
   :code:

або окрему відповідь:

.. http:example:: tutorial/get-answer.http
   :code:


Звернення можна задавати лише протягом періоду уточнень ``Tender.enqueryPeriod``.

.. http:example:: tutorial/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Реєстрація пропозиції
---------------------

Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.

Учасник може зареєструвати ставку для лоту №1 із статусом ``draft`` (чернетка):

.. http:example:: tutorial/register-bidder.http
   :code:

Та додамо відповіді на вимоги критеріїв:

.. http:example:: tutorial/add-requirement-responses-to-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: tutorial/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/upload-bid-proposal.http
   :code:

Спробуємо підтвердити пропозицію:

.. http:example:: tutorial/activate-bidder.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: tutorial/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозиціію, буде вимагатися новий підпиис:

.. http:example:: tutorial/activate-bidder-without-sign.http
   :code:

Завантаження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~

Для окремих документів учасники може встановити ознаку \“Опис рішення про закупівлю\” для цього потрібно передати ``isDescriptionDecision``

Спочатку завантажемо файл

.. http:example:: tutorial/upload-bid-descriptive-decision-proposal.http
   :code:

Потім встановити ``isDescriptionDecision``

.. http:example:: tutorial/mark-bid-doc-decision-proposal.http
   :code:

Конфіденційність
^^^^^^^^^^^^^^^^

Документи можуть бути або публічними, або приватними:

  1. Приватність документа можна змінити тільки для останньої версії.
  2. При завантаженні нової версії, налаштування приватності копіюються з попередньої версії документа.
  3. Налаштування приватності можна міняти тільки під час періоду подання пропозицій (зі статусом `active.tendering`).
  4. Якщо закупівля має статус `active.qualification`, переможець може завантажувати тільки публічні документи.

Завантажимо приватний документ:

.. http:example:: tutorial/upload-bid-private-proposal.http
   :code:

Щоб зробити документ "приватним", потрібно встановити поля `confidentiality` та `confidentialityRationale`.

Значенням поля `confidentiality` може бути або `buyerOnly` - документ приватний, або `public` - документ публічно доступний.

Вміст приватних документів (`buyerOnly`) закритий для всіх крім замовника і учасника, який подав ці документи.

Поле `confidentialityRationale` необхідне лише для приватних документів. Його значенням має бути пояснення причини конфіденційності документа (не менше ніж 30 символів).

Позначимо документ як "приватний":

.. http:example:: tutorial/mark-bid-doc-private.http
   :code:

Якщо документ має ознаку ``isDescriptionDecision`` то при встановлені конфіденційності поле ``confidentialityRationale`` можно опустити.

Позначимо документ як "приватний":

.. http:example:: tutorial/mark-bid-doc-decision-private.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: tutorial/bidder-documents.http
   :code:

.. _competitivedialogue_envelopes:


Пропозиція стає недійсною
~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі:

.. http:example:: tutorial/bidder-after-changing-tender.http
   :code:

Підтвердження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~~

Учасник повинен підтвердити свою пропозицію:

.. http:example:: tutorial/bidder-activate-after-changing-tender.http
   :code:

Для процедури конкурентного діалогу першого етапу потрібно хоча б 3 пропозиції:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:

Зареєструемо ще дві пропозиції:

.. http:example:: tutorial/register-3rd-bidder.http
   :code:

Пакетний режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~

У пакетному режимі (batch-mode) є можливість зареєструвати пропозицію одним запитом. Зареєструйте ще одну пропозицію:

.. http:example:: tutorial/register-4rd-bidder.http
   :code:


.. index:: Qualification

Кваліфікація пропозицій
-----------------------

Для першого етапу конкурентного діалогу необхідна кваліфікація пропозицій.

Переглянемо список кваліфікацій:


.. http:example:: tutorial/qualifications-listing.http
   :code:

Підтвердіть перші три пропозиції через кваліфікаційні об’єкти:

.. http:example:: tutorial/approve-qualification1.http
   :code:

.. http:example:: tutorial/approve-qualification2.http
   :code:

.. http:example:: tutorial/approve-qualification4.http
   :code:

Можна відхилити пропозицію:

.. http:example:: tutorial/reject-qualification3.http
   :code:

Та перевірити, що вже кваліфіковані пропозиції переключені в стан `active`:

.. http:example:: tutorial/qualificated-bids-view.http
   :code:

Відхилена пропозиція не присутня в списку `bids/`.

Можна отримати доступ до відхиленої пропозиції за її ідентифікатором `id`:

.. http:example:: tutorial/rejected-bid-view.http
   :code:

Замовник підтверджує кваліфікацію переходом до наступного статусу.

Перед схваленням рішення необхідно додати файл підпису до тендеру. Файл підпису повинен бути доданий до тендеру загалом. Якщо нема файлу підпису під час схвалення кваліфікації, ми побачимо помилку:

.. http:example:: tutorial/pre-qualification-sign-doc-is-required.http
   :code:

Файд підпису повинен мати `documentType: evaluationReports` та `title: *.p7s`. Додамо такий документ:

.. http:example:: tutorial/upload-evaluation-reports-doc.http
   :code:

Ще раз схвалимо кваліфікацію заявок:

.. http:example:: tutorial/pre-qualification-confirmation.http
   :code:

Зверніть увагу на період блокування в 10 днів під час `qualificationPeriod`.


Готовність до другого етапу
---------------------------

Коли ``qualificationPeriod`` період завершиться тендер змінить статус на ``active.stage2.pending``

Подивимося на наш тендер

.. http:example:: tutorial/stage2-pending.http
   :code:


Замовник може підтвердити свою готовність переходити на другий етап, змінивши стаус тендера на ``active.stage2.waiting``

.. http:example:: tutorial/stage2-waiting.http
   :code:


Отримаємо токен для другого етапу
---------------------------------

Коли статус тендеру(першого етапу) буду ``complete``, ми можемо отримати id другого етапу.

Подивимось на тендер і знайдемо поле ``stage2TenderID``

.. http:example:: tutorial/tender_stage1_complete.http
   :code:


Щоб робити зміни в другому етапі потрібно отримати токен.

.. http:example:: tutorial/tender_stage2_get_token.http
    :code:

Зробимо зміни на другому етапі
------------------------------

Добре, ми отримали токен, і можемо робити зміни в другому етапі. Спробуемо змінити статус ``draft.stage2`` на ``active.tendering``.


.. http:example:: tutorial/tender_stage2_modify_status.http
    :code:

Другий етап EU
--------------

.. toctree::
    :maxdepth: 1

    tutorial_stage2EU

Другий етап UA
--------------

.. toctree::
    :maxdepth: 1

    tutorial_stage2UA
