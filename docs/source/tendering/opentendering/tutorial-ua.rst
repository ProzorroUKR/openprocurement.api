.. _opentendering_tutorial_ua:

Туторіал: відкриті торги UA (``procedure.euPublished`` = ``false``)
===================================================================

.. index:: Tender

Конфігурація
------------

Набір можливих значень конфігурації для різновиду ``UA``:

.. csv-table::
   :file: csv/opentendering-ua/config.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Дозволені значення `procuringEntity.kind`
-----------------------------------------

.. csv-table::
   :file: csv/opentendering-ua/kind.csv
   :header-rows: 1

Створення закупівлі
-------------------

Особливість відкритих торгів за Законом № 4888 в тому, що разом з ``procurementMethodType`` = ``openTendering``
обов'язково передається об'єкт ``procedure`` з полем ``euPublished``, що визначає різновид
(``false`` - UA, ``true`` - EU). Без нього закупівлю створити не вдасться:

.. http:example:: http/opentendering-ua/tender-post-without-procedure.http
   :code:

Структура об'єкта ``procedure`` перевіряється схемою ``procedureExtensionScheme`` типу процедури зі standards:
``euPublished`` має бути булевим значенням, інші поля не допускаються:

.. http:example:: http/opentendering-ua/tender-post-invalid-procedure.http
   :code:

Значення конфігурації мають відповідати обраному різновиду. Спробуємо передати для ``UA`` мінімальний строк
подання пропозицій різновиду ``EU``:

.. http:example:: http/opentendering-ua/tender-post-invalid-config.http
   :code:

Введемо коректні data та config атрибути у поданому тілі:

.. http:example:: http/opentendering-ua/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `draft`. Тут неможливо встановити ``enquiryPeriod``, бо він буде призначений автоматично.

Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: http/opentendering-ua/blank-tender-view.http
   :code:

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Різновид не можна змінити після створення закупівлі:

.. http:example:: http/opentendering-ua/patch-procedure.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: http/opentendering-ua/tender-listing-no-auth.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу `active.tendering`

Закупівля може складатись із декількох лотів. Можна створити лот таким чином:

.. http:example:: http/opentendering-ua/tender-add-lot.http
   :code:

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: http/opentendering-ua/tender-add-relatedLot-to-item.http
   :code:

Активація закупівлі
-------------------

Спочатку нам потрібно додати вийняткові критерії до нашої закупівлі(:ref:`Про критерії ви можете дізнатися тут<criteria_operation>`)

.. http:example:: http/opentendering-ua/add-exclusion-criteria.http
   :code:

Шаблон договору визначається на рівні тендера: перед активацією обов'язково вказується або ``contractTemplateName``,
або документ з ``documentType: contractProforma``. Без них активація відхиляється:

.. http:example:: http/opentendering-ua/contract-template-required.http
   :code:

Додамо документ проєкту договору:

.. http:example:: http/opentendering-ua/add-contract-proforma-document.http
   :code:

Перед активацією тендера необхідно обов'язково додати файл підпису. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/opentendering-ua/notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/opentendering-ua/add-notice-document.http
   :code:

Після додавання необхідних критеріїв, проєкту договору та файлу підпису ми можемо активувати закупівлю:

.. http:example:: http/opentendering-ua/tender-activating.http
   :code:

Подивимось, що показує список закупівель. Різновид доступний у списку через ``opt_fields=procedure``:

.. http:example:: http/opentendering-ua/active-tender-listing-no-auth.http
   :code:

Ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату.

Редагування закупівлі
---------------------

Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: http/opentendering-ua/patch-items-value-periods.http
   :code:

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: http/opentendering-ua/tender-listing-after-patch.http
   :code:

Замовник не може редагувати закупівлю, якщо після змін до завершення періоду подання пропозицій залишається менше 4 повних календарних днів (день внесення змін не враховується). API таких змін не прийме.

.. http:example:: http/opentendering-ua/update-tender-after-enqiery.http
   :code:

Ось чому потрібно в тому самому запиті продовжити період подання пропозицій.

.. http:example:: http/opentendering-ua/update-tender-after-enqiery-with-update-periods.http
   :code:

Замовник може встановити забезпечення тендерної пропозиції:

.. http:example:: http/opentendering-ua/set-bid-guarantee.http
   :code:


.. index:: Document

Завантаження документів
-----------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: http/opentendering-ua/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції `документів`, щоб підтвердити дію:

.. http:example:: http/opentendering-ua/tender-documents.http
   :code:

Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: http/opentendering-ua/upload-award-criteria.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: http/opentendering-ua/tender-documents-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: http/opentendering-ua/update-award-criteria.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: http/opentendering-ua/tender-documents-3.http
   :code:


.. index:: Звернення, Question, Answer

Звернення
---------

Якщо закупівля має статус ``active.tendering`` та дата завершення періоду уточнень ``Tender.enquiryPeriod.endDate`` ще не прийшла, то зацікавлені учасники можуть подавати звернення чи просити уточнень умов закупівлі:

.. http:example:: http/opentendering-ua/ask-question.http
   :code:

Замовник може відповісти на них:

.. http:example:: http/opentendering-ua/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: http/opentendering-ua/list-question.http
   :code:

або окрему відповідь:

.. http:example:: http/opentendering-ua/get-answer.http
   :code:

Звернення можна задавати лише протягом періоду уточнень ``Tender.enquiryPeriod``

.. http:example:: http/opentendering-ua/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Реєстрація пропозиції
---------------------

Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.

Учасник може зареєструвати пропозицію для лоту №1 зі статусом ``draft`` (чернетка):

.. http:example:: http/opentendering-ua/register-bidder.http
   :code:

Та додамо відповіді на вимоги критеріїв:

.. http:example:: http/opentendering-ua/add-requirement-responses-to-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: http/opentendering-ua/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: http/opentendering-ua/upload-bid-proposal.http
   :code:

Спробуємо підтвердити пропозицію:

.. http:example:: http/opentendering-ua/activate-bidder.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: http/opentendering-ua/bidder-documents.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: http/opentendering-ua/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозицію, буде вимагатися новий підпис:

.. http:example:: http/opentendering-ua/activate-bidder-without-sign.http
   :code:

Пропозиція стає недійсною
~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі:

.. http:example:: http/opentendering-ua/bidder-after-changing-tender.http
   :code:

Підтвердження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~~

Учасник повинен підтвердити свою пропозицію:

.. http:example:: http/opentendering-ua/bidder-activate-after-changing-tender.http
   :code:

Для проведення аукціону потрібні щонайменше дві пропозиції. Зареєструємо другу:

.. http:example:: http/opentendering-ua/register-2nd-bidder.http
   :code:

Торги з однією пропозицією
~~~~~~~~~~~~~~~~~~~~~~~~~~

На відміну від legacy відкритих торгів, ``openTendering`` відбувається навіть з однією поданою пропозицією
(``minBidsNumber`` = 1). Якщо до завершення періоду подання зареєстровано лише одну пропозицію, аукціон не
проводиться, а закупівля переходить у ``active.qualification``:

.. http:example:: http/opentendering-ua/one-bid-switch-to-qualification.http
   :code:

Єдиний учасник одразу потрапляє на розгляд (``award`` у статусі ``pending``):

.. http:example:: http/opentendering-ua/one-bid-awards-list.http
   :code:


.. index:: Awarding, Qualification

Аукціон
-------

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: http/opentendering-ua/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: http/opentendering-ua/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників:

.. http:example:: http/opentendering-ua/bidder2-participation-url.http
   :code:


Аномально низька ціна
---------------------

Об’єкт award може містити milestone типу ``alp``

.. http:example:: http/opentendering-ua/get-awards-list.http
   :code:

Замовник не може змінити статус award до настання “milestone.dueDate”

.. http:example:: http/opentendering-ua/fail-disqualification.http
   :code:

Протягом цього часу учасник торгів може завантажувати документи ``evidence`` до своєї заявки

.. http:example:: http/opentendering-ua/post-evidence-document.http
   :code:


Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `eligible: True` та `qualified: True` - при переході award з `pending` в `active`

* `eligible: False` та `qualified: True` АБО `eligible: True` та `qualified: False` АБО `eligible: False` та `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` та `eligible` учасника:

.. http:example:: http/opentendering-ua/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` або `non-eligible` учасника:

.. http:example:: http/opentendering-ua/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/opentendering-ua/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: http/opentendering-ua/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/opentendering-ua/award-add-notice-document.http
   :code:

Кваліфікаційна комісія реєструє своє рішення:

.. http:example:: http/opentendering-ua/confirm-qualification.http
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

Для відміни скасування закупівлі, вам потрібно оновити статус скасування до `unsuccessful` з `draft` чи `pending`.

Дивіться структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

При скасуванні, замовник має визначити один з п'яти типів reasonType: `noDemand`, `unFixable`, `forceMajeure`, `expensesCut` або `noLocalization`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`.

.. http:example:: http/opentendering-ua/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище.

.. http:example:: http/opentendering-ua/update-cancellation-reasonType.http
   :code:

Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скасування.

Завантажити вміст файлу

.. http:example:: http/opentendering-ua/upload-cancellation-doc.http
   :code:

Зміна опису документа та інших властивостей

.. http:example:: http/opentendering-ua/patch-cancellation.http
   :code:

Завантажити нову версію документа

.. http:example:: http/opentendering-ua/update-cancellation-doc.http
   :code:

Проходження періоду оскарження
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для того щоб перейти до періоду оскарження потрібно змінити статус скасування з `draft` на `pending`.

Перед активацією запиту на скасування закупівлі необхідно додати файл підпису до `cancellation`. Якщо нема файлу підпису під час активації скасування, ми побачимо помилку:

.. http:example:: http/opentendering-ua/cancellation-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: cancellationReport` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/opentendering-ua/upload-cancellation-report-doc.http
   :code:

Змінимо статус скасування з `draft` на `pending`:

.. http:example:: http/opentendering-ua/pending-cancellation.http
   :code:

Коли скасування закупівлі в статусі `pending` замовнику забороняються всі дії по закупівлі.

Активація запиту та скасування закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо період оскарження (триває 10 днів) скінчився та не було ніяких скарг на скасування закупівлі або скарги були скасовані, то скасування автоматично змінює статус на `active`:

.. http:example:: http/opentendering-ua/active-cancellation.http
   :code:
