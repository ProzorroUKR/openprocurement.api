.. _cfaua_tutorial:

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

.. ПРЕЦЕДЕНТ Т1. Опублікувати оголошення

Дозволені значення `procuringEntity.kind`
-----------------------------------------

.. csv-table::
   :file: csv/kind.csv
   :header-rows: 1

Створення тендера
-----------------

Створімо тендерну пропозицію з мінімальним (обов'язковим для внесення) набором даних:

.. http:example:: tutorial/tender-post-attempt-json-data.http
   :code:

Вийшло! Тепер бачимо, що створено новий об'єкт. Код відповіді - `201` а заголовок відповіді `Location` вказує на місцезнаходження створеного об'єкта. Тіло відповіді показує інформацію про створену тендерну пропозицію: її внутрішнє `id` (що співпадає з сегментом `Location`), її офіційне `tenderID` та мітку дати `dateModified`, що вказує час, коли до тендерної пропозиції востаннє вносились зміни. Зверніть увагу на `procurementMethodType`. Важливо, що тендерна пропозиція створюється зі статусом `draft`.

Використаємо URL створеного об'єкта (заголовок відповіді `Location`):

Особливість процедури Закритої Рамкової Угоди UA полягає в тому, що ``procurementMethodType`` було змінено з ``belowThreshold`` на ``closeFrameworkAgreementUA``. Також тут немає можливості встановити ``enquiryPeriod``, оскільки він призначається автоматично.

.. http:example:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо ту ж відповідь, що і після створення закупівлі.

Подивимось, що показує список закупівель:

.. http:example:: tutorial/initial-tender-listing.http
   :code:

Ми поки не бачимо внутрішнього `id` закупівлі, тому що у списку відображаються закупівлі лише після статусу ``active.enquiries``

Ви можете додати додаткову :ref:`ContactPoint` і декілька :ref:`Item`. Також можна створити закупівлю з :ref:`Feature` (`https://prozorro-api-docs.readthedocs.io/uk/frameworkagreement/basic-actions/meat.html?highlight=features#announcing-meat`).

Та активувати заявку:
---------------------

Спочатку нам потрібно додати вийняткові критерії до нашої закупівлі(:ref:`Про критерії ви можете дізнатися тут<criteria_operation>`)

.. http:example:: tutorial/add-exclusion-criteria.http
   :code:

Після додавання необхідних критеріїв ми иожемо активувати закупівлю:

.. http:example:: tutorial/tender-activating.http
   :code:

Подивимось, що показує список закупівель:

.. http:example:: tutorial/active-tender-listing-no-auth.http
   :code:

Тепер ми бачимо внутрішнє `id` тендерної пропозиції (що можна використати для побудови повної URL-адреси коли додамо `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її мітку дати `dateModified`.


Внесення змін до тендера
------------------------

Оновимо тендерну пропозицію, додаючи інші важливі властивості:

.. http:example:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

Бачимо, що додані властивості об'єдналися з наявними даними щодо тенденої пропозиції. Також оновилась властивість `dateModified` і тепер відображає мітку дати останнього внесення змін.

Знову перевіряємо список і бачимо нову дату внесення змін:

.. http:example:: tutorial/tender-listing-after-patch.http
   :code:

Замовник може встановити тендерну гарантію:

.. http:example:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

На цьому етапі можна змінювати наступні поля: ``agreementDuration``, :ref:`item`, ``maxAwardsCount``, :ref:`ProcuringEntity`, ``tenderPeriod``, ``title``, ``title_ru``, ``title_en``, ``description``, ``description_ru``, ``description_en``, ``eligibilityCriteria``, ``procurementMethodRationale``, ``guarantee``, :ref:`feature`, :ref:`document`, :ref:`lot`.


Завантаження документації
-------------------------

Замовник може завантажити PDF файли у створену тендерну пропозицію. Завантаження має відбуватись згідно з правилами :ref:`upload`.

.. http:example:: tutorial/upload-tender-notice.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ створено. Можна додатково здійснити запит точки входу API колекції `documents`, щоб підтвердити дію:

.. http:example:: tutorial/tender-documents.http
   :code:

Єдиний елемент масиву описує завантажений документ. Можна завантажити більше документів:

.. http:example:: tutorial/upload-award-criteria.http
   :code:

Знову можна підтвердити, що завантажено два документа.

.. http:example:: tutorial/tender-documents-2.http
   :code:

Якщо сталася помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: tutorial/update-award-criteria.http
   :code:

І бачимо, що він замінив початкову версію документа:

.. http:example:: tutorial/tender-documents-3.http
   :code:


.. index:: Звернення, Question, Answer


.. ПРЕЦЕДЕНТ Т5. Задати питання

Звернення
---------

Поки тендерна пропозиція має статус ``active.tendering``, а момент ``Tender.enquiryPeriod.endDate`` ще не настав, зацікавлені сторони можуть подавати звернення:

.. http:example:: tutorial/ask-question.http
   :code:

Замовник може на них відповідати:

.. http:example:: tutorial/answer-question.http
   :code:

Можна отримати список запитань:

.. http:example:: tutorial/list-question.http
   :code:

Та окрему відповідь:

.. http:example:: tutorial/get-answer.http
   :code:


Звернення можна задавати лише під час ``Tender.enquiryPeriod``

.. http:example:: tutorial/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

.. ПРЕЦЕДЕНТ Т3. Подати пропозицію
.. ПРЕЦЕДЕНТ Т4. Внести зміну в пропозицію

Реєстрація цінової заявки
-------------------------

Покрокова реєстрація
~~~~~~~~~~~~~~~~~~~~

Коли тендерна пропозиція перебуває в статусі ``active.tendering``, можна реєструвати цінові заявки.

Учасник може зареєструвати заявку зі статусом `draft`:

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

Також учасник може подати ставку з неціновими критеріями - :ref:`parameter` (`https://prozorro-api-docs.readthedocs.io/uk/frameworkagreement/basic-actions/meat.html?highlight=features#bidding-in-meat`).

При кожному редагуванні вже поданої пропозиції, пропозиція буде переходити в статус `invalid` і її треба буде заново підписати:

.. http:example:: tutorial/patch-pending-bid.http
   :code:

Якщо ми спробуємо підтвердити пропозицію, буде вимагатися новий підпис:

.. http:example:: tutorial/activate-bidder-without-sign.http
   :code:

Конфіденційність
^^^^^^^^^^^^^^^^

Документи можуть мати як публічний, так і приватний доступ:

  1. Налаштування приватності можна змінити лише для останньої версії документу.
  2. Коли ви завантажуєте нову версію документу, налаштування приватності дублюються з попередньої версії.
  3. Налаштування приватності можна змінити лише під час `tenderPeriod` (у статусі `active.tendering`).
  4. Якщо тендерна пропозиція має статус `active.qualification`, то переможець може завантажити лише документи з публічним доступом.

Спробуймо завантажити документ з приватним доступом:

.. http:example:: tutorial/upload-bid-private-proposal.http
   :code:

Щоб документ визначався як "private", потрібно налаштувати поля `confidentiality` та `confidentialityRationale`.

Значення поля `confidentiality` може бути `buyerOnly` (документ лише з приватним доступом) або `public` (документ з публічним доступом).

Вміст приватних документів (`buyerOnly`) може бути доступним лише для замовника чи учасника, який їх завантажив.

Поле `confidentialityRationale` є обов'язковим до заповнення лише для приватних документів і повинне містити щонайменше 30 символів.

Позначмо документ як "private":

.. http:example:: tutorial/mark-bid-doc-private.http
   :code:

Є можливість перевірити завантажені документи:

.. http:example:: tutorial/bidder-documents.http
   :code:

.. _envelopes:

Завантаження документів, що стосуються вартості, терміну дії та кваліфікації
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Документи, що стосуються вартості і терміну дії угоди та підтвердження кваліфікації також є частиною Заявки але знаходяться в інших точках входу.

Щоб створити і/або отримати документ щодо вартості угоди, потрібно використати точку входу ``financial_documents``:

.. http:example:: tutorial/upload-bid-financial-document-proposal.http
   :code:

Отримуємо документи щодо вартості:

.. http:example:: tutorial/bidder-financial-documents.http
   :code:

Щоб створити і/або отримати документ щодо терміну дії угоди, потрібно використати точку входу ``eligibility_documents``:

.. http:example:: tutorial/upload-bid-eligibility-document-proposal.http
   :code:

Щоб створити і/або отримати документ щодо підтвердження кваліфікації, потрібно використати точку входу ``qualification_documents``:

.. http:example:: tutorial/upload-bid-qualification-document-proposal.http
   :code:

Якщо сталася помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: tutorial/upload-bid-qualification-document-proposal-updated.http
   :code:


Документація `Financial`та `qualification` стане загальнодоступною після закінчення аукціону. Документація щодо `Eligibility` стане загальнодоступною з початком прекваліфікаційного періоду.

Тут бачимо пропозицію учасника з усіма документами.

.. http:example:: tutorial/bidder-view-financial-documents.http
   :code:

Зверніть увагу, що документи, що стосуються вартості і терміну дії угоди та підтвердження кваліфікації зберігаються в атрибутах :ref:`Bid`.


Скасування заявки
~~~~~~~~~~~~~~~~~

Якщо до тендерної пропозиції вносяться зміни, то статуси усіх цінових заявок зміниться на ``invalid``. Так виглядатиме заявка учасника торгів після внесення змін до тендерної пропозиції:

.. http:example:: tutorial/bidder-after-changing-tender.http
   :code:

Підтвердження заявки
~~~~~~~~~~~~~~~~~~~~

Учасник має підтвердити подану пропозицію:

.. http:example:: tutorial/bidder-activate-after-changing-tender.http
   :code:

Учасник може змінити свою пропозицію, після її активації. Для цього він змінює value:amount (:ref:`value`). Також можливо модифікувати :ref:`parameter`, subContractors, :ref:`document`.

Процедура Закритої Рамкової Угоди UA вимагає щонайменше трьох учасників торгів, тож має бути зареєстровано щонайменше три цінові заявки, щоб перейти до етапу аукціону:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:


Пакетний режим реєстрації
~~~~~~~~~~~~~~~~~~~~~~~~~

Можна зареєструвати заявку з документами одним запитом:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification


.. ПРЕЦЕДЕНТ Т10. Провести прекваліфікацію

Кваліфікація заявок
-------------------

Процедура Закритої Рамкової Угоди UA вимагає кваліфікації заявок.

Складемо список кваліфікаційних вимог:


.. http:example:: tutorial/qualifications-listing.http
   :code:

Схвалюємо три заявки з допомогою об'єктів кваліфікації:

.. http:example:: tutorial/approve-qualification1.http
   :code:

.. http:example:: tutorial/approve-qualification2.http
   :code:

.. http:example:: tutorial/approve-qualification4.http
   :code:

Також можна відхилити заявку:

.. http:example:: tutorial/reject-qualification3.http
   :code:

Для того, щоб відхилити пропозицію, Замовник має вказати причину відхилення в полі ``description``.

І перевірити чи заявки, що пройшли кваліфікацію, переведені в статус `active`:

.. http:example:: tutorial/qualificated-bids-view.http
   :code:

Відхилена заявка не відображається у списку `bids/`.

Можемо знайти відхилену заявку за її id:

.. http:example:: tutorial/rejected-bid-view.http
   :code:

Замовник схвалює кваліфікацію заявок, перейшовши в наступний статус.

Перед схваленням рішення необхідно додати файл підпису до тендеру. Файл підпису повинен бути доданий до тендеру загалом. Якщо нема файлу підпису під час схвалення кваліфікації, ми побачимо помилку:

.. http:example:: tutorial/pre-qualification-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: evaluationReports` та `title: *.p7s`. Додамо такий документ:

.. http:example:: tutorial/upload-evaluation-reports-doc.http
   :code:

Ще раз схвалимо кваліфікацію заявок:

.. http:example:: tutorial/pre-qualification-confirmation.http
   :code:

Замовник може змінити ``status`` пропозиції на протилежний під час `active.prequalification`.

Зверніть увагу, що термін простою `qualificationPeriod` встановлюється на 10 днів.

.. ПРЕЦЕДЕНТ Т11. Брати участь в аукціоні

Аукціон
-------

Коли оголошується час проведення аукціону, будь-хто може подивитись, як він проходить. На аукціон можна зайти за адресою `Tender.lot.auctionUrl`:

.. http:example:: tutorial/auction-url.http
   :code:

Учасники торгів можуть отримати свої URL для доступу на аукціон через свої заявки :

.. http:example:: tutorial/bidder-participation-url.http
   :code:

`Bid.lotValues.participationUrl` має з'явитись у відповіді. Подібні але інші URL можна витягнути й для решти учасників:

.. http:example:: tutorial/bidder2-participation-url.http
   :code:

.. http:example:: tutorial/bidder4-participation-url.http
   :code:

.. ПРЕЦЕДЕНТ Т12. Визначити переможців

Підтвердження кваліфікації
--------------------------


Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `eligible: True` та `qualified: True` - при переході award з `pending` в `active`

* `eligible: False` та `qualified: True` АБО `eligible: True` та `qualified: False` АБО `eligible: False` та `qualified: False` - при переході award з `pending` в `unsuccessful`

Спробуємо відхилити авард для `qualified` та `eligible` учасника:

.. http:example:: tutorial/unsuccessful-qualified-award.http
   :code:

Спробуємо винести рішення по переможцю по аварду для `non-qualified` або `non-eligible` учасника:

.. http:example:: tutorial/activate-non-qualified-award.http
   :code:

Перед прийняттям рішення по переможцю необхідно обов'язково додати файл підпису до аварду. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: tutorial/award-notice-document-required.http
   :code:

Така сама логіка при відхилені аварду:

.. http:example:: tutorial/award-unsuccessful-notice-document-required.http
   :code:

Файл підпису має тип документу `documentType: notice` та розширення `title: *.p7s`. Додамо файл підпису:

.. http:example:: tutorial/award-add-notice-document.http
   :code:

Кваліфікаційна комісія отримує список претендентів до кваліфікації

.. http:example:: tutorial/qualifications-list.http
   :code:

Додає підпис і реєструє своє рішення через такий виклик на кожного `award`:

.. http:example:: tutorial/confirm-qualification.http
   :code:

Комісія також може дискваліфікувати переможця викликом ``{'data': {'status': 'cancelled'}}``

.. http:example:: tutorial/patch-award-cancelled.http
   :code:

Бачимо, що згенеровано новий award в статусі `pending` для цього ж учасника.

.. http:example:: tutorial/qualifications-list2.http
   :code:

Тепер можна підписати і патчити award зі статусу `pending` в `unsuccessful`.

.. http:example:: tutorial/patch-award-unsuccessful.http
   :code:

У випадку переведення award з ``unsuccessful`` в ``cancelled``, тендер переходить на початок статусу ``active.qualification``, всі об'єкти :ref:`award` стають ``cancelled`` і генеруються нові об'єкти.

Тепер можна патчити award зі статусу `pending` в `unsuccessful`.

.. http:example:: tutorial/patch-award-unsuccessful-cancelled.http
   :code:

Нові award в статусі `pending` генеруються для кожного учасника.

.. http:example:: tutorial/qualifications-list3.http
   :code:

Нарешті ми підтверджуємо всі award в статусі `pending`:

.. http:example:: tutorial/confirm-qualification2.http
   :code:

Замовник має вказати причину дискваліфікації Учасника в полі ``description``.

Замовник може продовжити процес кваліфікації :ref:`award`, якщо це необхідно. Замовник має завантажити документи про це.

Завершенням кваліфікаї є переведення процедури в статус `active.qualification.stand-still`.


.. ПРЕЦЕДЕНТ Т13. Додати документи з цінами

Завантаження документу з переліком цін за одиницю товару
--------------------------------------------------------

Коли тендерна пропозиція переходить в статус `active.awarded`, створюється :ref:`Agreement_cfaua`, і переможцям аукціону надається п'ять робочих днів на завантаження переліку цін за одиницю кожного предмету закупівлі.

.. http:example:: tutorial/upload-prices-document.http
   :code:

Внесення цін за предмет закупівлі стороною замовника
----------------------------------------------------

Список об'єктів :ref:`Agreement_cfaua` можна отримати з допомогою цього виклику

.. http:example:: tutorial/agreements-list.http
   :code:

Лише один контракт створюється на одного переможця аукціону, що пройшов кваліфікацію

Сторона замовника може отримати список об'єктів :ref:`Contract` для внесення цін за предмет закупівлі з допомогою такого виклику

.. http:example:: tutorial/agreement-contracts-list.http
   :code:

Внесення цін за одиницю товару можливе лише для всіх предметів закупівлі 'items' разом

.. http:example:: tutorial/agreement-contract-unitprices1.http
   :code:

.. http:example:: tutorial/agreement-contract-unitprices2.http
   :code:

.. http:example:: tutorial/agreement-contract-unitprices3.http
   :code:

Також стороні замовника дозволено виключити переможця з рамкової угоди, перевівши контракт в статус ``{'data': {'status': 'unsuccessful'}}``

Для успішного підписання Рамкової угоди необхідно щонайменше 3 активних контракта

Рамкову угоду можна підписати лише з настанням моменту `agreement.contractPeriod.clarificationsUntil`

Замовник може заповнити інформацію про ``agreementNumber``.


Завантаження документації щодо угоди
------------------------------------

Тепер можна завантажити документацію, що стосується угоди. Спробуймо завантажити документ, що стосується угоди:

.. http:example:: tutorial/tender-agreement-upload-document.http
   :code:

Код відповіді `201 Created` і заголовок `Location` підтверджують, що цей документ було додано.

Перегляньмо список документів стосовно угоди:

.. http:example:: tutorial/tender-agreement-get-documents.http
   :code:

Можемо додати ще один документ стосовно угоди:

.. http:example:: tutorial/tender-agreement-upload-second-document.http
   :code:

Код відповіді `201 Created` і заголовок `Location` підтверджують, що другий документ також було додано.

За замовчуванням, мова документації - українська. Це можна змінити і встановити іншу мову для документу, встановивши відповідний мовнй код в полі `language` (доступні варіанти: ``uk``, ``en``, ``ru``). Можна також встановити поля назви документа (наприклад, `title_en`) та його опису (наприклад, `description_en`). Детальніше в структурі даних :ref:`Document`.

.. http:example:: tutorial/tender-agreement-patch-document.http
    :code:

Перегляньмо список усіх доданих документів стосовно угоди:

.. http:example:: tutorial/tender-agreement-get-documents-again.http
   :code:

Подивімося на окремий документ щодо угоди:

.. http:example:: tutorial/tender-agreement-get.http
    :code:


Встановлення дати підписання угоди
----------------------------------

Є можливість встановити потрібну дату підписання угоди. Якщо дата не встановлена, то вона буде згенерована під час реєстрації угоди.

.. http:example:: tutorial/tender-agreement-sign-date.http
   :code:

Реєстрація угоди
----------------

.. http:example:: tutorial/tender-agreement-sign.http
   :code:

Скасування тендера
------------------

Замовник може скасувати закупівлю у будь-який момент (крім закупівель у статусі `active.auction` чи у кінцевому стані, наприклад, `unsuccessful`, `canceled`, `complete`).

Для цього потрібно виконати такі кроки:

1. Приготуйте запит на скасування
2. Наповніть його протоколом про причини скасування
3. Проходження періоду оскарження(триває 10 днів)
4. Скасуйте тендерну пропозицію через подані причини.

Запит на скасування, який не пройшов активації (4-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її.

Для відміни скасування закупівлі, вам потрібно оновити статус скасування до `unsuccessful` з `draft` чи `pending`

Детальніше в структурі запиту :ref:`cancellation`.

Формування запиту на скасування
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ви повинні передати змінні `reason` та `reasonType`, `status` у стані `draft`.

При скасуванні, замовник має визначити один з чотирьох типів reasonType: `noDemand`, `unFixable`, `forceMajeure` aбо `expensesCut`.

`id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`.

.. http:example:: tutorial/prepare-cancellation.http
   :code:


Наповнення запиту на скасування протоколом та супровідною документацією
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Цей крок обов'язковий. Без документів ви не можете оновити статус скарги.

Завантажуємо вміст файлу

.. http:example:: tutorial/upload-cancellation-doc.http
   :code:

Змінюємо опис документу та інші властивості

.. http:example:: tutorial/patch-cancellation.http
   :code:

Завантажуємо нову версію документа

.. http:example:: tutorial/update-cancellation-doc.http
   :code:

Проходження періоду оскарження
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для того щоб перейти до періоду оскарження потрібно змінити статус скасування з `draft` на `pending`.

Перед активацією запиту на скасування закупівлі необхідно додати файл підпису до `cancellation`. Якщо нема файлу підпису під час активації скасування, ми побачимо помилку:

.. http:example:: tutorial/cancellation-sign-doc-is-required.http
   :code:

Файл підпису повинен мати `documentType: cancellationReport` та `title: *.p7s`. Додамо такий документ:

.. http:example:: tutorial/upload-cancellation-report-doc.http
   :code:

Змінимо статус скасування з `draft` на `pending`:

.. http:example:: tutorial/pending-cancellation.http
   :code:

Коли скасування закупівлі в статусі `pending` замовнику забороняються всі дії по закупівлі.

Активуємо запит і скасовуємо тендерну пропозицію
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо період оскарження(триває 10 днів) скінчився та не було ніяких скарг на скасування закупівлі або скарги були скасовані, то скасування автоматично змінює статус на `active`

Переведення угоди в статус `unsuccessful`
-----------------------------------------

Замовник може змінити статус угоди на `unsuccessful`.

.. http:example:: tutorial/agreement-unsuccessful.http
   :code:

Переведення тендера в статус `unsuccessful`.

.. http:example:: tutorial/tender-unsuccessful.http
   :code:
