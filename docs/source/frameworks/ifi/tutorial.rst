.. _framework_ifi_tutorial:

Туторіал
========

Створення кваліфікації
----------------------

Створимо кваліфікацію:

.. http:example:: tutorial/create-framework.http
   :code:

Ми отримали код відповіді `201 Created`, заголовок `Location` і тіло з додатковими полями.

Кваліфікацію було створено у статусі `draft`. У цьому статусі будь-яке поле, окрім технічних, може бути змінено.

.. http:example:: tutorial/patch-framework-draft.http
   :code:

Завантаження документації
-------------------------

Замовник може завантажити PDF файл у створениу кваліфікацію. Завантаження повинно відбуватись згідно правил :ref:`upload`.

.. http:example:: tutorial/upload-framework-document.http
   :code:

Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції документів, щоб підтвердити дію:

.. http:example:: tutorial/framework-documents.http
   :code:

І знову можна перевірити, що є два завантажених документа.

.. http:example:: tutorial/upload-framework-document-2.http
   :code:

Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії:

.. http:example:: tutorial/upload-framework-document-3.http
   :code:

І ми бачимо, що вона перекриває оригінальну версію:

.. http:example:: tutorial/get-framework-document-3.http
   :code:

Активація кваліфікації
----------------------

Наступний крок - змінити статус кваліфікації на `active`.

`qualificationPeriod.endDate` має бути у проміжку не менш ніж 365 днів і не більш ніж 1461 днів з моменту активації.

Перед активацією до кваліфікації має бути додано хоча б один документ та підпис.

.. http:example:: tutorial/patch-framework-draft-to-active.http
   :code:

Після активації кваліфікації будуть розраховані періоди:

`enquiryPeriod` - перші 10 повних робочих днів з моменту активації.

`period` - період, коли постачальники можуть подавати заявки.

`qualificationPeriod` - останні 30 повних календарних днів кваліфікації. У цей період постачальники не можуть подавати нові заявки, але ще приймаються рішення щодо попередньо поданих заявок.

.. http:example:: tutorial/get-framework.http
   :code:

Перевіримо, що містить реєстр кваліфікації:

.. http:example:: tutorial/framework-listing.http
   :code:

Відображається  `id` - внутрішній ідентифікатор та мітка часу `dateModified`.

Зміна кваліфікації
------------------

У статусі `active` можна змінювати лише деякі поля: `telephone`, `name`, `email` для `procuringEntity.contactPoint`, `description` and `documents`.

.. http:example:: tutorial/patch-framework-active.http
   :code:

Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: tutorial/framework-listing.http
   :code:

Зміна qualificationPeriod в активному відборі
---------------------------------------------

Також у статусі `active` можна замінити `endDate` поле в `qualificationPeriod`, але це можна зробити вже через окремий ендпоінт.

Існують наступні валідації для зміни терміну дії відбору `qualificationPeriod.endDate`:

* qualificationPeriod.endDate couldn't be less than 30 full calendar days from now
* qualificationPeriod.endDate couldn't be more than 1461 full calendar days from now

Зміну терміну дії відбору може виконувати лише `framework_owner` (власник кваліфікації) використовуючи ченжи.

Поля, які необхідно заповнити для зміни терміну дії відбору:

* `qualificationPeriod.endDate` (in `change.modifications`)
* `rationale`
* `rationaleType`
* `documents` (optional)

Спробуємо змінити `qualificationPeriod.endDate` на ранню дату:

.. http:example:: tutorial/patch-framework-active-qualification-period-too-soon.http
   :code:

Спробуємо змінити `qualificationPeriod.endDate` на пізню дату:

.. http:example:: tutorial/patch-framework-active-qualification-period-too-late.http
   :code:

Успішна зміна терміну дії відбору:

.. http:example:: tutorial/patch-framework-active-qualification-period.http
   :code:

Необхідно вказати параметр opt_context=true для того, щоб отримати додаткову інформацію з відбору для підписання змін:

.. http:example:: tutorial/get-change-sign-data.http
   :code:

Для детальної інформації про відображення інформації для підписів, дивитися тут: :ref:`sign-data`.

Тепер необхідно додати документ підпису до змін:

.. http:example:: tutorial/sign-framework-active-qualification-period.http
   :code:

Якщо було змінено поле `qualificationPeriod.endDate` - всі періоди будуть перераховані.

Подивимося тепер на відбір:

.. http:example:: tutorial/get-framework-after-qualification-period-modified.http
   :code:

Тепер у відборі існує новий об'єкт `changes` з попереднім значенням `qualificationPeriod.endDate` і новим значенням. Всі зміни терміну дії відбору будуть збережені в цьому об'єкті.

Реєстрація заявки
-----------------

Після активації кваліфікації, користувачі можуть зареєструвати свої заявки в період з `framework.period.startDate` до `framework.period.endDate`:

.. http:example:: tutorial/register-submission.http
   :code:

Ми отримали код відповіді `201 Created`, заголовок `Location` і тіло з додатковими полями.


Завантаження документації по заявці
-----------------------------------

Документи можливо завантажити/оновити тільки до заявки у статусі `draft.`

Усі операції над документами такі ж як у кваліфікації:

.. http:example:: tutorial/upload-submission-document.http
   :code:

.. http:example:: tutorial/get-submission-documents.http
   :code:

Конфіденційні файли у заявці
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Документи можуть бути публічними та конфіденційними.

Приховання (конфіденційність) може бути застосована/змінена для документів у заявці у статусі `draft`. Обов'язковим є додавання поля обґрунтування `confidentialityRationale` для `confidentiality: buyerOnly`.

Додамо документи з `confidentiality: buyerOnly` і подивимося, що ми маємо:

.. http:example:: tutorial/upload-submission-conf-docs-wo-rationale.http
   :code:

Додамо поле обґрунтування `confidentialityRational`:

.. http:example:: tutorial/upload-submission-conf-docs.http
   :code:

Власник заявки та власник відбору бачить такі документи і може завантажиити їх:

.. http:example:: tutorial/get-submission-conf-docs-by-owner.http
   :code:

Всі інші користувачі не можуть переглянути документ:

.. http:example:: tutorial/get-submission-conf-docs-by-public.http
   :code:

Ніхто окрім власника заявки та власника відбору не може викачати документ:

.. http:example:: tutorial/upload-submission-conf-doc-by-public.http
   :code:


Видалення заявки
----------------

Заявка може бути видалена лише у статусі `draft`:

.. http:example:: tutorial/deleting-submission.http
   :code:


Оновлення заявки
----------------

Заявка може бути оновлена лише у статусі `draft`:

.. http:example:: tutorial/updating-submission.http
   :code:

Активація заявки
----------------

Заявку можна активувати лише до настання `period.endDate`

.. http:example:: tutorial/activating-submission.http
   :code:

Після активації заявки, автоматично створюється об'єкт рішення по заявці і заповнюється поле `qualificationID` в заявці.

Перевіримо, що містить реєстр заявки:

.. http:example:: tutorial/submission-listing.http
   :code:

Перевіримо об'єкт рішення по заявці:

.. http:example:: tutorial/get-qualification.http
   :code:

Всі операції над об'єктом рішення по заявці може виконувати лише `framework_owner` (власник кваліфікації).


Завантаження документації до рішення по заявці
----------------------------------------------

Документи можливо завантажити/оновити тільки до рішення у статусі `pending`.

Усі операції над документами такі ж як у кваліфікації:

.. http:example:: tutorial/upload-qualification-document.http
   :code:

.. http:example:: tutorial/get-qualification-documents.http
   :code:


Відміна рішення по заявці
-------------------------

Рішення можливо відмінити лише у статусі `pending`.

Перед відміною рішення необхідно додати файл підпису до кваліфікації. Якщо нема файлу підпису під час відміни, ми побачимо помилку:

.. http:example:: tutorial/evaluation-reports-document-required-for-cancelling.http
   :code:

Файл підпису повинен мати `documentType: evaluationReports` та `title: *.p7s`. Додамо такий документ:

.. http:example:: tutorial/add-evaluation-reports-document-for-cancelling.http
   :code:

Тепер можна відмінити рішення по заявці:

.. http:example:: tutorial/unsuccessful-qualification.http
   :code:

Після відміни рішення, пов'язана завявка змінює статус з `active` на `complete`.

Перевіримо що сталося з заявками після відміни рішення:

.. http:example:: tutorial/get-submissions-by-framework-id.http
   :code:

Підтвердження рішення по заявці
-------------------------------

Рішення можливо погодити лише у статусі `pending`.

Перед погодженням необхідно додати файл підпису до кваліфікації. Якщо нема файлу підпису під час активації, ми побачимо помилку:

.. http:example:: tutorial/evaluation-reports-document-required.http
   :code:

Файл підпису повинен мати `documentType: evaluationReports` та `title: *.p7s`. Додамо такий документ:

.. http:example:: tutorial/add-evaluation-reports-document.http
   :code:

Тепер можна підтвердити рішення по заявці:

.. http:example:: tutorial/activation-qualification.http
   :code:

Після підтвердження рішення по заявці, якщо це було перше затверджене рішення система створює реєстр з контрактом, в іншому випадку система додає контракт до реєстру.

Перевіримо кваліфікацію:

.. http:example:: tutorial/get-framework-with-agreement.http
   :code:

Ви можете побачити, що в кваліфікації з'явилось поле `agreementID`, тож давайте перевіримо реєстр:

.. http:example:: tutorial/get-agreement.http
   :code:

Як ви можете побачити реєстр в статусі `active` та має контракт, щож ми можемо побачити цей реєстр в потоці даних:

.. http:example:: tutorial/agreement-listing.http
   :code:


Перевіримо, що містить реєстр рішення по заявці:

.. http:example:: tutorial/qualification-listing.http
   :code:

Перевіримо всі рішення по заявці до данної кваліфікації:

.. http:example:: tutorial/get-qualifications-by-framework-id.http
   :code:


Завершення кваліфікації
-----------------------

Завершення кваліфікації відбувається автоматично після настання дати `qualificationPeriod.endDate`.

PATCH запит з новим значенням `qualificationPeriod.endDate` дозволяє завершити фрейморк раніше запланованого часу, але не раніше 30 повних календарних днів з моменту зміни `qualificationPeriod.endDate`.