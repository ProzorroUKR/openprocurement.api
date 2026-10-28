.. _opentendering_tutorial_eu:

Туторіал: відкриті торги EU (``procurementAspects`` = ``["EU"]``)
=================================================================

.. index:: Tender

Конфігурація
------------

Набір можливих значень конфігурації для різновиду ``EU``:

.. csv-table::
   :file: csv/opentendering-eu/config.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Дозволені значення `procuringEntity.kind`
-----------------------------------------

.. csv-table::
   :file: csv/opentendering-eu/kind.csv
   :header-rows: 1

Створення закупівлі
-------------------

Разом з ``procurementMethodType`` = ``openTendering`` обов'язково передається різновид
``procurementAspects`` = ``["EU"]``. Значення конфігурації мають відповідати різновиду: для ``EU``
попередня кваліфікація обов'язкова, тому ``hasPrequalification`` = ``false`` відхиляється:

.. http:example:: http/opentendering-eu/tender-post-invalid-config.http
   :code:

Оголошення різновиду ``EU`` додатково публікується англійською мовою, тому поля ``procuringEntity.name_en``,
``procuringEntity.identifier.legalName_en``, ``procuringEntity.contactPoint.name_en`` та ``items[].description_en``
обов'язкові:

.. http:example:: http/opentendering-eu/tender-post-without-english-fields.http
   :code:

Введемо коректні data та config атрибути у поданому тілі:

.. http:example:: http/opentendering-eu/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `draft`. Тут неможливо встановити ``enquiryPeriod``, бо він буде призначений автоматично.

Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: http/opentendering-eu/blank-tender-view.http
   :code:

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Різновид не можна змінити після створення закупівлі:

.. http:example:: http/opentendering-eu/patch-procurement-aspects.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: http/opentendering-eu/tender-listing-no-auth.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу `active.tendering`

Закупівля може складатись із декількох лотів. Можна створити лот таким чином:

.. http:example:: http/opentendering-eu/tender-add-lot.http
   :code:

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: http/opentendering-eu/tender-add-relatedLot-to-item.http
   :code:

Активація закупівлі
-------------------

Спочатку нам потрібно додати вийняткові критерії до нашої закупівлі(:ref:`Про критерії ви можете дізнатися тут<criteria_operation>`)

.. http:example:: http/opentendering-eu/add-exclusion-criteria.http
   :code:

Шаблон договору визначається на рівні тендера: перед активацією обов'язково вказується або ``contractTemplateName``,
або документ з ``documentType: contractProforma``. Додамо документ проєкту договору:

.. http:example:: http/opentendering-eu/add-contract-proforma-document.http
   :code:

Перед активацією тендера необхідно обов'язково додати файл підпису. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/opentendering-eu/notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/opentendering-eu/add-notice-document.http
   :code:

Після додавання необхідних критеріїв, проєкту договору та файлу підпису ми можемо активувати закупівлю:

.. http:example:: http/opentendering-eu/tender-activating.http
   :code:

Подивимось, що показує список закупівель. Різновид доступний у списку через ``opt_fields=procurementAspects``:

.. http:example:: http/opentendering-eu/active-tender-listing-no-auth.http
   :code:

Ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату.

Редагування закупівлі
---------------------

Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: http/opentendering-eu/patch-items-value-periods.http
   :code:

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: http/opentendering-eu/tender-listing-after-patch.http
   :code:

Замовник не може редагувати закупівлю, якщо після змін до завершення періоду подання пропозицій залишається менше 7 повних календарних днів (день внесення змін не враховується). API таких змін не прийме.

.. http:example:: http/opentendering-eu/update-tender-after-enqiery.http
   :code:

Ось чому потрібно в тому самому запиті продовжити період подання пропозицій (`tenderPeriod`).

.. http:example:: http/opentendering-eu/update-tender-after-enqiery-with-update-periods.http
   :code:

Замовник може встановити забезпечення тендерної пропозиції:

.. http:example:: http/opentendering-eu/set-bid-guarantee.http
   :code:


.. index:: Document

Завантаження документів
-----------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: http/opentendering-eu/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів (`documents`), щоб підтвердити дію:

.. http:example:: http/opentendering-eu/tender-documents.http
   :code:

Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: http/opentendering-eu/upload-award-criteria.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: http/opentendering-eu/tender-documents-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: http/opentendering-eu/update-award-criteria.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: http/opentendering-eu/tender-documents-3.http
   :code:


.. index:: Звернення, Question, Answer

Звернення
---------

Якщо закупівля має статус ``active.tendering`` та дата завершення періоду уточнень ``Tender.enquiryPeriod.endDate`` ще не прийшла, то зацікавлені учасники можуть подавати звернення чи просити уточнень умов закупівлі:

.. http:example:: http/opentendering-eu/ask-question.http
   :code:

Замовник може відповісти на них:

.. http:example:: http/opentendering-eu/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: http/opentendering-eu/list-question.http
   :code:

або окрему відповідь:

.. http:example:: http/opentendering-eu/get-answer.http
   :code:

Звернення можна задавати лише протягом періоду уточнень ``Tender.enquiryPeriod``

.. http:example:: http/opentendering-eu/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Реєстрація пропозиції
---------------------

Реєстрація пропозиції
~~~~~~~~~~~~~~~~~~~~~

Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.

Учасник може зареєструвати ставку для лоту №1 із статусом ``draft`` (чернетка):

.. http:example:: http/opentendering-eu/register-bidder.http
   :code:

Та додамо відповіді на вимоги критеріїв:

.. http:example:: http/opentendering-eu/add-requirement-responses-to-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: http/opentendering-eu/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: http/opentendering-eu/upload-bid-proposal.http
   :code:

Спробуємо підтвердити пропозицію:

.. http:example:: http/opentendering-eu/activate-bidder.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: http/opentendering-eu/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозицію, буде вимагатися новий підпис:

.. http:example:: http/opentendering-eu/activate-bidder-without-sign.http
   :code:

Конфіденційність
~~~~~~~~~~~~~~~~

Завантажимо документ:

.. http:example:: http/opentendering-eu/upload-bid-private-proposal.http
   :code:

Щоб зробити документ "приватним", потрібно встановити поля `confidentiality` та `confidentialityRationale`.

Значенням поля `confidentiality` може бути або `buyerOnly` - документ приватний, або `public` - документ публічно доступний.

Вміст приватних документів (`buyerOnly`) закритий для всіх крім замовника і учасника, який подав ці документи.

Поле `confidentialityRationale` необхідне лише для приватних документів. Його значенням має бути пояснення причини конфіденційності документа (не менше ніж 30 символів).

Позначимо документ як "приватний":

.. http:example:: http/opentendering-eu/mark-bid-doc-private.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: http/opentendering-eu/bidder-documents.http
   :code:

Завантаження документів, що підтверджують відповідність, фінансових та кваліфікаційних документів
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Документи, що підтверджують відповідність, фінансові та кваліфікаційні документи також є частиною пропозиції, але зберігаються в різних точках входу.

Для того, щоб створити і/або отримати фінансові документи потрібно використати точку входу ``financial_documents``:

.. http:example:: http/opentendering-eu/upload-bid-financial-document-proposal.http
   :code:

Отримати фінансові документи:

.. http:example:: http/opentendering-eu/bidder-financial-documents.http
   :code:

Для того, щоб створити і/або отримати документи, що підтверджують відповідність потрібно використати точку входу ``eligibility_documents``:

.. http:example:: http/opentendering-eu/upload-bid-eligibility-document-proposal.http
   :code:

Для того, щоб створити і/або отримати документи, що підтверджують кваліфікацію, потрібно використати точку входу ``qualification_documents``:

.. http:example:: http/opentendering-eu/upload-bid-qualification-document-proposal.http
   :code:

`Фінансові` та `кваліфікаційні` документи будуть публічно доступні після аукціону. Документи, `що підтверджують відповідність`, будуть публічно доступні на етапі попередньої кваліфікації.

Пропозиція учасника зі всіма документами.

.. http:example:: http/opentendering-eu/bidder-view-financial-documents.http
   :code:

Зверніть увагу, що документи, що підтверджують відповідність, фінансові та кваліфікаційні документи зберігаються у `eligibilityDocuments`, `financialDocuments` та `qualificationDocuments` атрибутах :ref:`Bid` відповідно.

Пропозиція стає недійсною
~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі:

.. http:example:: http/opentendering-eu/bidder-after-changing-tender.http
   :code:

Підтвердження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~~

Учасник повинен підтвердити свою пропозицію:

.. http:example:: http/opentendering-eu/bidder-activate-after-changing-tender.http
   :code:

Торги відбуваються навіть з однією пропозицією (``minBidsNumber`` = 1): з однією допущеною пропозицією аукціон не проводиться, а переможець визначається одразу. Для аукціону потрібні щонайменше дві допущені пропозиції, тому зареєструємо другу:

.. http:example:: http/opentendering-eu/register-2nd-bidder.http
   :code:

Пакетний режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~

У пакетному режимі (batch-mode) є можливість зареєструвати пропозицію одним запитом. Зареєструйте ще одну пропозицію:

.. http:example:: http/opentendering-eu/register-3rd-bidder.http
   :code:


.. index:: Awarding, Qualification

Попередня кваліфікація пропозицій
---------------------------------

Для різновиду ``EU`` необхідна попередня кваліфікація пропозицій: після завершення періоду подання закупівля
переходить у ``active.pre-qualification``, пропозиції розкриваються без ціни.

Переглянемо список кваліфікацій:

.. http:example:: http/opentendering-eu/qualifications-listing.http
   :code:

Підтвердіть перші дві пропозиції через кваліфікаційні об’єкти:

.. http:example:: http/opentendering-eu/approve-qualification1.http
   :code:

.. http:example:: http/opentendering-eu/approve-qualification2.http
   :code:

Можна відхилити пропозицію:

.. http:example:: http/opentendering-eu/reject-qualification3.http
   :code:

Та перевірити, що вже кваліфіковані пропозиції переключені в стан `active`:

.. http:example:: http/opentendering-eu/qualificated-bids-view.http
   :code:

Відхилена пропозиція не присутня в списку `bids/`.

Можна отримати доступ до відхиленої пропозиції за її ідентифікатором `id`:

.. http:example:: http/opentendering-eu/rejected-bid-view.http
   :code:

Замовник підтверджує кваліфікацію переходом до наступного статусу.

Перед схваленням рішення необхідно додати файл підпису до тендеру. Файл підпису повинен бути доданий до тендеру загалом. Якщо нема файлу підпису під час схвалення кваліфікації, ми побачимо помилку:

.. http:example:: http/opentendering-eu/pre-qualification-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: evaluationReports` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/opentendering-eu/upload-evaluation-reports-doc.http
   :code:

Ще раз схвалимо кваліфікацію заявок:

.. http:example:: http/opentendering-eu/pre-qualification-confirmation.http
   :code:

Зверніть увагу на період оскарження в 10 календарних днів під час `qualificationPeriod`.

Аукціон
-------

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: http/opentendering-eu/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: http/opentendering-eu/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників:

.. http:example:: http/opentendering-eu/bidder2-participation-url.http
   :code:

Підтвердження кваліфікації
--------------------------

Після аукціону формується список авардів:

.. http:example:: http/opentendering-eu/get-awards-list.http
   :code:

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `eligible: True` та `qualified: True` - при переході award з `pending` в `active`

* `eligible: False` та `qualified: True` АБО `eligible: True` та `qualified: False` АБО `eligible: False` та `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` та `eligible` учасника:

.. http:example:: http/opentendering-eu/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` або `non-eligible` учасника:

.. http:example:: http/opentendering-eu/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/opentendering-eu/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: http/opentendering-eu/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/opentendering-eu/award-add-notice-document.http
   :code:

Кваліфікаційна комісія реєструє своє рішення:

.. http:example:: http/opentendering-eu/confirm-qualification.http
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

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у статусі `active.auction` чи у кінцевому стані, наприклад, `unsuccessful`, `canceled`, `complete`).

Для цього потрібно виконати наступні кроки:

1. Приготуйте запит на скасування.
2. Наповніть його протоколом про причини скасування.
3. Проходження періоду оскарження(триває 10 днів)
4. Скасуйте закупівлю через подані причини.

Запит на скасування, який не пройшов активації (4-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Для відміни скасування закупівлі, вам потрібно оновити статус скасування до `unsuccessful` з `draft` чи `pending`

Дивіться структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

При скасуванні, замовник має визначити один з п'яти типів reasonType: `noDemand`, `unFixable`, `forceMajeure`, `expensesCut` або `noLocalization`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`.

.. http:example:: http/opentendering-eu/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище.

.. http:example:: http/opentendering-eu/update-cancellation-reasonType.http
   :code:

Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скасування.

Завантажте вміст файлу

.. http:example:: http/opentendering-eu/upload-cancellation-doc.http
   :code:

Змініть опис документа та інші властивості

.. http:example:: http/opentendering-eu/patch-cancellation.http
   :code:

Завантажте нову версію документа

.. http:example:: http/opentendering-eu/update-cancellation-doc.http
   :code:

Проходження періоду оскарження
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для того щоб перейти до періоду оскарження потрібно змінити статус скасування з `draft` на `pending`.

Перед активацією запиту на скасування закупівлі необхідно додати файл підпису до `cancellation`. Якщо нема файлу підпису під час активації скасування, ми побачимо помилку:

.. http:example:: http/opentendering-eu/cancellation-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: cancellationReport` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/opentendering-eu/upload-cancellation-report-doc.http
   :code:

Змінимо статус скасування з `draft` на `pending`:

.. http:example:: http/opentendering-eu/pending-cancellation.http
   :code:

Коли скасування закупівлі в статусі `pending` замовнику забороняються всі дії по закупівлі.

Активація запиту та скасування закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо період оскарження (триває 10 днів) скінчився та не було ніяких скарг на скасування закупівлі або скарги були скасовані, то скасування автоматично змінює статус на `active`:

.. http:example:: http/opentendering-eu/active-cancellation.http
   :code:
