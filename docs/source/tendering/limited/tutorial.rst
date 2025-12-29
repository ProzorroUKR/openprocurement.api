.. _limited_tutorial:

Туторіал
========

Конфігурація
------------

Набір можливих значень конфігурації для `reporting`:

.. csv-table::
   :file: csv/config-reporting.csv
   :header-rows: 1

Набір можливих значень конфігурації для `negotiation`:

.. csv-table::
   :file: csv/config-negotiation.csv
   :header-rows: 1

Набір можливих значень конфігурації для `negotiation.quick`:

.. csv-table::
   :file: csv/config-negotiation-quick.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Дозволені значення `procuringEntity.kind`
-----------------------------------------

Набір можливих значень `procuringEntity.kind` для `reporting`

.. csv-table::
   :file: csv/kind-reporting.csv
   :header-rows: 1

Набір можливих значень `procuringEntity.kind` для `negotiation`

.. csv-table::
   :file: csv/kind-negotiation.csv
   :header-rows: 1

Набір можливих значень `procuringEntity.kind` для `negotiation.quick`

.. csv-table::
   :file: csv/kind-negotiation-quick.csv
   :header-rows: 1

Створення закупівлі
-------------------

Можна створити три процедури:
 * ``reporting`` - процедура звітування про укладений договір (без періоду очікування скарг)
 * ``negotiation`` - переговорна процедура з десятиденним періодом очікування скарг перед реєстрацією угоди
 * ``negotiation.quick`` - переговорна процедура за нагальною потребою з п’ятиденним періодом очікування скарг перед реєстрацією угоди


Створення закупівлі для процедури звітування про укладений договір
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Щоб створити закупівлю за процедурою **звітування про укладений договір**, потрібно встановити значення ``reporting`` для ``procurementMethodType``.

Для процедури **звітування про укладений договір** додавання поля `causeDetails` до тендеру є обов’язковим, якщо поле `procurmentMethodRationale` пусте, в полі `procuringEntity.kind` вказано щось відмінне від `other` та очікувана вартість перевищує поріг:

    * 100 000 для товарів,
    * 200 000 для послуг,
    * 1 500 000 для робіт.

Спробуємо створити тендер з очікуваною вартістю більше ніж поріг та без поля `procurementMethodRationale`:

.. http:example:: http/tutorial/create-tender-reporting-invalid.http
   :code:

Поле `code` обов'язкове для заповнення, тому заборонено передавати тільки `causeDetails.description`:

.. http:example:: http/tutorial/create-tender-reporting-invalid-cause-details.http
   :code:

І навпаки поле `description` обов'язкове для заповнення, якщо вказане `causeDetails.code`:

.. http:example:: http/tutorial/create-tender-reporting-cause-details-description-required.http
   :code:

Додамо до тендеру поле `causeDetails` і після цього створимо закупівлю:

.. http:example:: http/tutorial/create-tender-reporting-procuringEntity.http
   :code:

Ми отримали код відповіді `201 Created`, заголовок `Location` і тіло з додатковим ідентифікатором `id`, `tenderID` та властивість `dateModified` - дату, що показує час, коли закупівля востаннє модифікувалась.

Перевіримо, що містить реєстр закупівель:

.. http:example:: http/tutorial/tender-listing-after-procuringEntity.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу `active`.


Створення закупівлі для переговорної процедури
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Щоб створити закупівлю за **переговорною** процедурою, потрібно встановити значення ``negotiation`` для ``procurementMethodType``.

.. http:example:: http/tutorial/create-tender-negotiation-procuringEntity.http
   :code:


Створення закупівлі для переговорної процедури за нагальною потребою
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Щоб створити закупівлю для **переговорної процедури за нагальною потребою**, потрібно встановити значення ``negotiation.quick`` для ``procurementMethodType``.

.. http:example:: http/tutorial/create-tender-negotiation-quick-procuringEntity.http
   :code:


Активація закупівлі
~~~~~~~~~~~~~~~~~~~

Для активації закупівель **reporting**, **negotiation**, **negotiation.quick** їх потрібно перевести до статусу ``active``:

.. http:example:: http/tutorial/tender-activating.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: http/tutorial/active-tender-listing-after-procuringEntity.http
   :code:

Відображається  `id` - внутрішній ідентифікатор (який можна використовувати, щоб побудувати повну URL-адресу, додаючи `http://api-sandbox.openprocurement.org/api/0/tenders/` на початку) та мітка часу `dateModified`.


Модифікація закупівлі
~~~~~~~~~~~~~~~~~~~~~

Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей:

.. http:example:: http/tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість dateModified, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: http/tutorial/tender-listing-after-patch.http
   :code:


.. index:: Document

Завантаження документації
-------------------------

Замовник може завантажити документи у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: http/tutorial/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено.

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: http/tutorial/update-tender-notice.http
   :code:

Визначення переможця
--------------------

Додаємо інформацію про постачальника
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Спосіб додавання інформації про постачальника однаковий для всіх процедур.

Замовник реєструє інформацію про постачальника для процедури **звітування про укладений договір**:

.. http:example:: http/tutorial/tender-award.http
   :code:

Замовник реєструє інформацію про постачальника для **переговорної** процедури:

.. http:example:: http/tutorial/tender-negotiation-award.http
   :code:

Ви можете побачити, що згенеровано запис ``complaintPeriod`` із полем ``startDate``.

Замовник реєструє інформацію про постачальника для переговорної процедури за нагальною потребою:

.. http:example:: http/tutorial/tender-negotiation-quick-award.http
   :code:

Визначення переможця для **переговорної процедури за нагальною потребою** також має запис ``complaintPeriod`` із полем ``startDate``.


Завантаження документів щодо визначення переможця
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Завантажувати документи щодо визначення переможця можна лише до того, як рішення про визначення переможця буде підтверджено. Спробуємо додати такий документ:

.. http:example:: http/tutorial/tender-award-upload-document.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ додано.

Переглянемо документи пов’язані із визначенням переможця:

.. http:example:: http/tutorial/tender-award-get-documents.http
   :code:

Тепер спробуємо додати ще один документ щодо визначення переможця:

.. http:example:: http/tutorial/tender-award-upload-second-document.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що ще один документ було додано.

Тепер переглянемо знову усі документи пов’язані із визначенням переможця:

.. http:example:: http/tutorial/tender-award-get-documents-again.http
   :code:


Підтвердження переможця процедури
---------------------------------

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

Для **reporting** процедур файл підпису авардів не вимагається.

Замовник повинен підтвердити своє рішення про визначення переможця:

.. http:example:: http/tutorial/tender-award-approve.http
   :code:

Підтвердження визначення переможця для **переговорної** процедури
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/tutorial/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: http/tutorial/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису має тип документу `documentType: notice` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: http/tutorial/award-add-notice-document.http
   :code:

Тепер замовник повинен підтвердити своє рішення про визначення переможця:

.. http:example:: http/tutorial/tender-negotiation-award-approve.http
   :code:

Різниця між початковою (``startDate``) та кінцевою (``endDate``) датою запису ``complaintPeriod`` для **переговорної** процедури становить 10 днів.

Підтвердження визначення переможця для **переговорної процедури за нагальною потребою** процедури:

.. http:example:: http/tutorial/tender-negotiation-quick-award-approve.http
   :code:

Різниця між початковою ( ``startDate``) та кінцевою (``endDate``) датою запису ``complaintPeriod`` для **переговорної процедури за нагальною потребою** становить 5 днів.

.. index:: Налаштування угоди

Налаштування угоди
------------------

Усі операції над угодою перенесені до :ref:`base-contracting`


Реєстрація угоди
~~~~~~~~~~~~~~~~

Угода про закупівлю за процедурою **звітування про укладений договір** може бути зареєстрована одразу після підтвердження визначення переможця:

.. http:example:: http/tutorial/tender-contract-sign.http
   :code:

Угода про закупівлю за **переговорною** процедурою може бути зареєстрована одразу після `періоду очікування скарг` (десятиденний період після підтвердження визначення переможця):

.. http:example:: http/tutorial/tender-negotiation-contract-sign.http
   :code:

Угода про закупівлю для **переговорної процедури за нагальною потребою** може бути зареєстрована одразу після `періоду очікування скарг` (п’ятиденний період після підтвердження визначення переможця):

.. http:example:: http/tutorial/tender-negotiation-quick-contract-sign.http
   :code:

Конфіденційні файли у контракті
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Під час створення тендеру замовник з випадаючого списку підстав застосування звіту про договір про закупівлю у формі обирає один з пунктів (`causeDetails.code` в залежності від `procurementMethodType`). У випадку застосування однієї з наведених підстав, в такому звіті мають бути приховані файли (documents), які замовник завантажує до контракту та змін до договору (`"documentOf": "contract"` та `"documentOf": "change"`).

Документи мають бути конфіденційними якщо звіт має одну з перерахованих підстав (`causeDetails.code`):

    * criticalInfrastructure
    * civilProtection
    * RNBO
    * naturalGas
    * UZ
    * defencePurchase

і має один з перерахованих типів документів:

    * contractSigned - Підписаний договір
    * contractAnnexe - Додатки до договору

Приховання (конфіденційність) має бути застосована для documents, у випадку застосування наведених підстав. Обов'язковим є додавання поля обґрунтування `confidentialityRationale` для `confidentiality: buyerOnly`.

Додамо документи до контракту і виставимо в полі `confidentiality` значення `public`:

.. http:example:: http/tutorial/tender-reporting-contract-conf-docs-as-public.http
   :code:

Змінимо `confidentiality` на `buyerOnly` і подивимося, що ми маємо:

.. http:example:: http/tutorial/tender-reporting-contract-conf-docs-wo-rationale.http
   :code:

Додамо поле обґрунтування `confidentialityRational`:

.. http:example:: http/tutorial/tender-reporting-contract-conf-docs.http
   :code:

Власник звіту бачить такі документи і може завантажиити їх:

.. http:example:: http/tutorial/get-tender-reporting-contract-conf-docs-by-owner.http
   :code:

Всі інші користувачі не можуть переглянути документ:

.. http:example:: http/tutorial/get-tender-reporting-contract-conf-docs-by-public.http
   :code:

Ніхто окрім власника звіту не може викачати документ:

.. http:example:: http/tutorial/upload-tender-reporting-contract-conf-doc-by-public.http
   :code:

Скасування закупівлі
--------------------

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у статусі `active.auction` чи у кінцевому стані, наприклад, `usuccesfull`, `canceled`, `complete`).

Для цього потрібно виконати наступні кроки:

1. Приготуйте запит на скасування
2. Заповніть його протоколом про причини скасування
3. 3. Проходження періоду оскарження(триває 10 днів), тільки для `negotiation` та `negotiation.quick`
4. Скасуйте закупівлю через подані причини.

Запит на скасування, який не пройшов активації (4-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Для відміни скасування закупівлі, вам потрібно оновоить статус скасування до `unsuccessful` з `draft` чи `pending`.

Див. структуру запиту :ref:`cancellation` для більш детальної інформації.

Формування запиту на скасування для `reporting` процедури
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

При скасуванні, замовник має визначити один з чотирьох типів reasonType: `noDemand`, `unFixable`, `forceMajeure` aбо `expensesCut`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`.

.. http:example:: http/tutorial/prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище.

.. http:example:: http/tutorial/update-cancellation-reasonType.http
   :code:

Формування запиту на скасування для `negotiation` та `negotiation.quick` процедури
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

При скасуванні, замовник має визначити один з п'яти типів reasonType: `noObjectiveness`,  `unFixable`, `noDemand`, `expensesCut` та `dateViolation`.

.. http:example:: http/tutorial/negotiation-prepare-cancellation.http
   :code:

Ви можете виправити тип на будь-який що вказаний вище.

.. http:example:: http/tutorial/negotiation-update-cancellation-reasonType.http
   :code:


Наповнення протоколом та іншою супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скарги.

Завантажте зміст файлу

.. http:example:: http/tutorial/upload-cancellation-doc.http
   :code:

Якщо потрібно, змініть опис документа та інші властивості


.. http:example:: http/tutorial/patch-cancellation.http
   :code:

Завантажте нову версію документа


.. http:example:: http/tutorial/update-cancellation-doc.http
   :code:

Проходження періоду оскарження(тільки для `negotiation` та `negotiation.quick`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для того щоб перейти до періоду оскарження потрібно змінити стаутс скасування з `draft` на `pending`.

.. http:example:: http/tutorial/pending-cancellation.http
   :code:

Коли скасування закупівлі в статусі `pending` замовнику зобороняються всі дії по закупівлі.

Активація запиту та скасування закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо період оскарження(триває 10 днів) скінчився та не було ніяких скарг на скасування закупівлі або скарги були скасовані, то скасування автоматично зміює статус на `active`.