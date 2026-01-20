.. _pricequotation_tutorial:

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

Дозволені значення `procuringEntity.kind`
-----------------------------------------

.. csv-table::
   :file: csv/kind.csv
   :header-rows: 1

Створення закупівлі
-------------------

Введемо data атрибут у поданому тілі:

.. http:example:: http/tender-post-attempt-json-data.http
   :code:

Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `draft`.

.. note::

    Користувач отримує `access`: `token` з яким доступні операції ролі Замовника.

Процедура Запиту цінових пропозицій має ``procurementMethodType``: ``priceQuotation`` та ``procurementMethod``: ``selective``.

Використаємо URL створеного об’єкта (заголовок відповіді `Location`):

.. http:example:: http/blank-tender-view.http
   :code:

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Модифікація закупівлі
---------------------

Замовник може відредагувати закупівлю перед публікацією. Давайте оновимо закупівлю, доповнюючи її усіма іншими необхідними властивостями:

.. http:example:: http/patch-tender-data.http
   :code:

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: http/tender-listing-after-patch.http
   :code:

Публікація закупівлі (стара логіка через PQ бот)
------------------------------------------------
   
Після створення Замовник публікує процедуру, змінивши статус на `draft.publishing`, де робот **priceQuotationBot** запускає перевірку процедури та доповнює процедуру додатковими даними, отриманими з бази даних електронних каталогів ProZorro, включаючи `shortListedFirms`.

.. http:example:: http/publish-tender.http
   :code:


Після успішної валідації priceQuotationBot переводить процедуру в статус: `active.tendering`

.. http:example:: http/tender-after-bot-active.http
   :code:

У разі, якщо процедура не пройде перевірку через недійсні параметри, вона буде переведена в статус: `draft.unsuccessful` за допомогою **priceQuotationBot**.

.. http:example:: http/tender-after-bot-unsuccessful.http
   :code:

.. index:: Document

Активація закупівлі
-------------------

Після створення Замовник може активувати закупівлю, змінивши статус на `active.tendering`.

Перед активацією тендера необхідно обов'язково додати файл підпису. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/add-notice-document.http
   :code:

Під час активації на ЦБД спрацьовують наступні перевірки:

* Наявність профілю товару в каталозі

* Профіль повинен мати статус `active` або `general`

* Наявність відповідного договору

* Перевірка, що угода в профілі та пов’язана угода в тендері однакові

* Угода не повинна бути розірвана (статус terminated)


Якщо Замовник спробує активувати процедуру PQ з неіснуючим профілем у каталозі, ми побачимо помилку:

.. http:example:: http/tender-with-non-existed-profile.http
   :code:

Якщо профіль не активний, ми побачимо помилку:

.. http:example:: http/tender-with-non-active-profile.http
   :code:

Якщо угода (agreement) в профілі та угода в тендері не однакові, буде згенеровано наступну помилку:

.. http:example:: http/tender-agreement-mismatch-in-profile.http
   :code:

Якщо угода розірвана:

.. http:example:: http/tender-agreement-terminated.http
   :code:

Якщо процедура PQ відповідає всім вимогам, вона буде переведена в статус `active.tendering`:

.. http:example:: http/tender-active.http
   :code:


Подача пропозицій
-----------------

Реєстрація пропозиції
~~~~~~~~~~~~~~~~~~~~~
Статус закупівлі ``active.tendering`` дозволяє подання пропозицій.

Якщо `tenderer` в пропозиції не є кваліфікованим учасником в угоді, то ми побачимо помилку під час подання пропозиції:

.. http:example:: http/register-bidder-not-member.http
   :code:

.. note::

    Для типу закупівлі priceQuotation існує валідація: сума добутків по позиціям (`item.quantity * item.unit.value.amount`) повинна бути більше 0, і може відрізнятись в нижню сторону від bid.value.amount не більше ніж на 20%.

Якщо сума добутків цін за одиницю менше ніж нетто значення`bid.value.amount` (`bid.value.amount * 1.2`), учасник побачить помилку:

.. http:example:: http/register-bidder-invalid-unit-value.http
   :code:

Якщо позиція (`item`) в закупівлі посилається на категорію чи профіль, учасник має обов'язково вказувати продукт для цієї позиції. Якщо продукт не вказаний, ми побачимо помилку:

.. http:example:: http/register-bidder-without-item-product.http
   :code:

Учасник може зареєструвати пропозицію зі статусом ``draft`` (чернетка):

.. http:example:: http/register-bidder.http
   :code:

.. note::

    Користувач отримує `access`: `token` з яким доступні операції ролі Постачальника.


і підтвердити її, перевівши у ``pending`` статус:

.. http:example:: http/activate-bidder.http
   :code:

Якщо `tenderer` в пропозиції не є кваліфікованим учасником в угоді, то ми побачимо помилку під час подання пропозиції:

.. http:example:: http/register-bidder-not-member.http
   :code:

Модифікація пропозиції
~~~~~~~~~~~~~~~~~~~~~~
   
Пропозиція може бути оновленою до закінчення тендерного періоду.

.. http:example:: http/patch-bidder.http
   :code:

Видалення пропозиції
~~~~~~~~~~~~~~~~~~~~

Поки не завершився період подання пропозицій постачальник має можливість видаляти свою пропозицію.

Додамо нову пропозицію до тендеру:

.. http:example:: http/register-2nd-bid.http
   :code:

У постачальника є змога видалити її, якщо була допущена помилка:

.. http:example:: http/delete-2nd-bid.http
   :code:

Пропозиція відсутня в тендері після видалення:

.. http:example:: http/get-deleted-bid.http
   :code:
   
Завантаження пропозиції
~~~~~~~~~~~~~~~~~~~~~~~

Потім учасник повинен завантажити документ(и) пропозиції:

.. http:example:: http/upload-bid-proposal.http
   :code:

Можна перевірити завантажені документи:

.. http:example:: http/bidder-documents.http
   :code:

Закінчення періоду подання пропозицій
-------------------------------------

По закінченню періоду подання пропозицій (active.tendering) система знову перевіряє статус учасника у agreement. Якщо досі `аctive` - bid отримує `status:active`, якщо інший статус - пропозиція падає у статус `invalid`.

Припустимо, що другий постачальник в угоді був дискваліфікований під час періоду `active.tendering`.

Подивимося на статуси наших пропозицій після закінчення періоду `active.tendering`. Остання пропозиція, в якій постачальник був дискваліфікований в угоді, тепер має статус `invalid`:

.. http:example:: http/active-tendering-end-bids.http
   :code:
   
.. index:: Awarding

Процес визначення переможця
---------------------------

Після закінчення тендерного періоду, система автоматично створює ``award`` у статусі ``pending`` для пропозиції з найбільш економічно вигідною ціною.

.. http:example:: http/awards-listing.http
   :code:

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `qualified: True` - при переході award з `pending` в `active`

* `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` учасника:

.. http:example:: http/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` учасника:

.. http:example:: http/activate-non-qualified-award.http
   :code:

Замовник може прийняти `award` змінивши його статус на `active`.

.. http:example:: http/award-active.http
   :code:

Поглянемо на список `awards`:

.. http:example:: http/awards-listing-after-activation.http
   :code:

Замовник може відхилити `award` після прийняття змінивши його статус на `cancelled`:

.. http:example:: http/award-cancelled.http
   :code:

Після відхилення `award` система створює `другий award` для цієї пропозиції у статусі `pending`:

.. http:example:: http/awards-listing-after-cancellation.http
   :code:

Якщо пропозиція Учасника з найменшою ціною відповідає вимогам, Замовник завантажує документ, що підтверджує його рішення і визнає пропозицію Переможцем `(awards:status:active)`. Якщо не відповідає, Замовник завантажує протокол, що підтверджує його рішення про відхилення Учасника та відхиляє таку пропозицію `(awards:status:unsuccessful)`. Система приводить до оцінки наступного за ціною Учасника `(awards:status:pending)`.

Відхилимо `award` змінивши його статус на  `unsuccessful`.

.. http:example:: http/award-unsuccesful.http
   :code:

В цьому випадку `Award` буде наданий до наступної пропозиції з найбільш економічно вигідною ціною.

Поглянемо на список `awards`:

.. http:example:: http/awards-listing-after-unsuccesful.http
   :code:

Замовник може прийняти `award` другого учасника змінивши його статус на  `active`.

.. http:example:: http/award-active-2.http
   :code:

Поглянемо на список `awards`:

.. http:example:: http/awards-listing-after-activation-2.http
   :code:

.. note::

    У випадку переходу `award` останньої пропозиції у статус `unsuccessful` процедура набуде кінцевий статус: **`unsuccessful`**.


.. index:: Налаштування угоди

Налаштування угоди
------------------

В режимі Е-Контрактінгу угода створюється безпосередньо в системі угод.

.. note::
    Деякі дані для забезпечення сумісності будуть дублюватись в закупівлі до тих пір, поки угода не буде активована.

Більше дізнатись про роботу з Е-Контрактінгом в системі угод можна в розділі :ref:`contracting_tutorial`.

   
Відміна закупівлі
-----------------

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у кінцевому стані, наприклад, `unsuccessful`, `cancelled`, `complete`).

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

При скасуванні, замовник має визначити один з чотирьох типів reasonType: `noDemand`, `unFixable`, `forceMajeure` aбо `expensesCut`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`:

.. http:example:: http/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище.

.. http:example:: http/update-cancellation-reasonType.http
     :code:

Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус закупівлі.

Завантажити вміст файлу

.. http:example:: http/upload-cancellation-doc.http
   :code:

Зміна опису документа та інших властивостей


.. http:example:: http/patch-cancellation.http
   :code:

Завантажити нову версію документа


.. http:example:: http/update-cancellation-doc.http
   :code:

Активація запиту на відміну закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Перед активацією запиту на скасування закупівлі необхідно додати файл підпису до `cancellation`. Якщо нема файлу підпису під час активації скасування, ми побачимо помилку:

.. http:example:: http/cancellation-sign-doc-is-required.http
   :code:

Файд підпису повинен мати `documentType: cancellationReport` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/upload-cancellation-report-doc.http
   :code:

Активуємо запит на скасування закупівлі:

.. http:example:: http/active-cancellation.http
   :code:
