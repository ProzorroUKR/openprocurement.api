.. _requestforproposal_tutorial:

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

Набір можливих значень `procuringEntity.kind` для `requestForProposal`
----------------------------------------------------------------------

.. csv-table::
   :file: csv/kind.csv
   :header-rows: 1

Закупівля з контролером
-----------------------

Ви можете отримати інформацію тут: :ref:`requestforproposal_inspector_tutorial`

Створення закупівлі
-------------------
Для тендеру `requestForProposal` замовник може зазначити, що був попередній відбір учасників та вказати id agreement.

Використаємо `agreement` для прикладу:

.. http:example:: http/tutorial/view-agreement-1-contract.http
   :code:

Ми можемо створити тендер, вказавши цей `agreement`:

.. http:example:: http/tutorial/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу на `procurementMethodType`, а також на те, що закупівля створюється зі статусом `draft`.

Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: http/tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Подивимось, що показує список закупівель:

.. http:example:: http/tutorial/initial-tender-listing.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу `active.enquiries`

Закупівля може складатись із декількох лотів. Можна створити лот таким чином:

.. http:example:: http/tutorial/tender-add-lot.http
   :code:

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: http/tutorial/tender-add-relatedLot-to-item.http
   :code:

Активація закупівлі
~~~~~~~~~~~~~~~~~~~

Для активації процедури потрібно перевести її статус в ``active.enquiries``:

.. http:example:: http/tutorial/tender-activating.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: http/tutorial/active-tender-listing-no-auth.http
   :code:

Ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату.


Створення другої закупівлі
--------------------------

Попередня закупівля була створена лише з обов’язковими полями. Тепер додамо закупівлю з максимально допустимим набором даних при створенні (тендер повинен бути у статусі `created`).

.. http:example:: http/tutorial/create-tender-procuringEntity.http
   :code:

І знову код відповіді `201 Created`,  заголовок `Location` і тіло з додатковим `id`, `tenderID`, та властивість `dateModified`.

Перевіримо, що містить реєстр закупівель:

.. http:example:: http/tutorial/tender-listing-after-procuringEntity.http
   :code:

Дійсно, в нас зараз є дві закупівлі.

Можливо створювати закупівлю з полем `funders`, яке є необов'язковим:

.. http:example:: http/tutorial/create-tender-funders.http
   :code:


Модифікація закупівлі
---------------------

Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: http/tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: http/tutorial/tender-listing-after-patch.http
   :code:

Замовник може встановити забезпечення тендерної пропозиції:

.. http:example:: http/tutorial/set-bid-guarantee.http
   :code:

Також можна оновлювати закупівлю шляхом додавання поля `funders`:

.. http:example:: http/tutorial/patch-tender-funders.http
   :code:

Замовник не може редагувати `tenderPeriod.endDate`, якщо залишилось менше 4 днів до завершення періоду подання пропозицій. API таких змін не прийме.

.. http:example:: http/tutorial/update-tender-after-enquiry.http
   :code:

Ось чому потрібно продовжити період подання пропозицій (`tenderPeriod`) на мінімум 4 дні.

.. http:example:: http/tutorial/update-tender-after-enquiry-with-update-periods.http
   :code:


.. index:: Document

Завантаження документації
-------------------------

Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: http/tutorial/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції `документів`, щоб підтвердити дію:

.. http:example:: http/tutorial/tender-documents.http
   :code:


Додамо нове поле `documentType` з параметром `technicalSpecifications` до вже завантаженого документа.

.. http:example:: http/tutorial/tender-document-add-documentType.http
   :code:

Успіх! Код відповіді `200 OK` підтверджує, що поле `documentType` з параметром `technicalSpecifications` було додано.


Ось основний перелік полів, які можна змінити для документа.

* documentOf
* language
* documentType
* title
* title_en
* description
* description_en
* format
* relatedItem


Ми можемо змінити декілька з них:

.. http:example:: http/tutorial/tender-document-edit-docType-desc.http
   :code:

Ви могли помітити що `dateModified` оновлюється при зміні інформації про документ.


Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів:

.. http:example:: http/tutorial/upload-award-criteria.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: http/tutorial/tender-documents-2.http
   :code:


Раніше ми оновлювали деталі документа. Також можливо змінити сам (файл) документ. Для цього ми можемо завантажити нову версію:

.. http:example:: http/tutorial/update-award-criteria.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: http/tutorial/tender-documents-3.http
   :code:

Зауважте, що `datePublished` поле також було змінено. Воно пов'язано з файлом документа і вказує на момент його додавання.


Є можливість переглянути всі версії усіх документів. Для цього використайте `?all=1` параметр.

.. http:example:: http/tutorial/tender-documents-3-all.http
   :code:

У відповіді ми бачимо одну версію Notice документа і дві версії AwardCriteria документа. Обидві версії мають однакове значення `id` поля, але різні для `datePublished`. Вони вказують на час додавання цих версій.

Зауважте, поля `datePublished` та `dateModified` дорівнюють одне одному.


Також зверніть увагу поля з інформацією про документ, що можна змінювати, - title, language, description і тд. Всі вони застосовані до нової версії. Попередня версія зберігає свої значення.


.. index:: Уточнення, Question, Answer

Уточнення
---------

Коли закупівля має статус `active.enquiry`, зацікавлені сторони можуть подавати звернення:

.. http:example:: http/tutorial/ask-question.http
   :code:

Замовник може на них відповісти:

.. http:example:: http/tutorial/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: http/tutorial/list-question.http
   :code:

та окрему відповідь:

.. http:example:: http/tutorial/get-answer.http
   :code:


.. index:: Bidding

Реєстрація пропозиції
---------------------

Покроковий режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Коли приходить ``Tender.tenderingPeriod.startDate``, Закупівля отримує статус `active.tendering`, що дозволяє реєстрацію пропозицій.

Учасник може зареєструвати пропозицію для лота №1 у статусі `draft` (чернетка):

.. http:example:: http/tutorial/register-bidder.http
   :code:

Після цього учасник має підтвердити пропозицію, перевівши у ``pending`` статус. Якщо учасник резидент (`tenderers.identifier.scheme = 'UA-EDR'`), то перед підтвердженням пропозиції він має накласти електронний підпис. Якщо файлу підписа не знайдено під час підтвердження, буде наступна помилка:

.. http:example:: http/tutorial/activate-bidder-without-proposal.http
   :code:

Файл підпису має тип документу `documentType: proposal` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: http/tutorial/upload-bid-proposal.http
   :code:

Спробуємо підтвердити пропозицію:

.. http:example:: http/tutorial/activate-bidder.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: http/tutorial/bidder-documents.http
   :code:

Якщо закупівля не мультивалютна, тоді існує додаткова перевірка, що сума всіх `items.unit.value` не може перевищувати ціну пропозиції:

.. http:example:: http/tutorial/register-bidder-invalid.http
   :code:

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: http/tutorial/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозиціію, буде вимагатися новий підпиис:

.. http:example:: http/tutorial/activate-bidder-without-sign.http
   :code:

Пакетний режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~

У пакетному режимі (batch-mode) є можливість зареєструвати пропозицію одним запитом:

.. http:example:: http/tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Аукціон
-------

Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`:

.. http:example:: http/tutorial/auction-url.http
   :code:

Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції:

.. http:example:: http/tutorial/bidder-participation-url.http
   :code:

Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників.

.. http:example:: http/tutorial/bidder2-participation-url.http
   :code:

Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `qualified: True` - при переході award з `pending` в `active`

* `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` учасника:

.. http:example:: http/tutorial/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` учасника:

.. http:example:: http/tutorial/activate-non-qualified-award.http
   :code:

Кваліфікаційна комісія реєструє своє рішення через такий виклик:

.. http:example:: http/tutorial/confirm-qualification.http
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

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у кінцевому стані, наприклад, `usuccesfull`, `canceled`, `complete`).

Для цього потрібно виконати наступні кроки:

1. Приготуйте запит на скасування
2. Наповніть його протоколом про причини скасування
3. Скасуйте закупівлю через подані причини

Запит на скасування, який не пройшов активації (3-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Див. структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`:

.. http:example:: http/tutorial/prepare-cancellation.http
   :code:


Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скарги.

Завантаження вмісту файлу

.. http:example:: http/tutorial/upload-cancellation-doc.http
   :code:

Зміна опису документа та інших властивостей

.. http:example:: http/tutorial/patch-cancellation.http
   :code:

Завантаження нової версії документа

.. http:example:: http/tutorial/update-cancellation-doc.http
   :code:

Активація запиту та скасування закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: http/tutorial/create-tender-funders.http
   :code:
