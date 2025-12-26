.. _competitivedialogue_mulitlot_tutorial:

Туторіал для багатолотової закупівлі
====================================


Створення закупівлі
-------------------

Створимо закупівлю:

.. http:example:: multiple_lots_tutorial/tender-post-attempt-json-data.http
   :code:

Тепер ми бачимо, що новий об’єкт було створено. Код відповіді - `201`, заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `active.tendering`.

Особливість відкритих торгів з публікацією англ. мовою в тому, що ``procurementMethodType`` було змінено з ``belowThreshold`` на ``aboveThresholdEU``.  Також тут неможливо встановити ``enquiryPeriod``, бо він буде призначений автоматично.

Закупівля може складатись із декількох лотів. Можна створити лот таким чином:

.. http:example:: multiple_lots_tutorial/tender-add-lot.http
   :code:

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: multiple_lots_tutorial/tender-add-relatedLot-to-item.http
   :code:

Перегляньте список закупівель:

.. http:example:: multiple_lots_tutorial/tender-listing-no-auth.http
   :code:

або перегляньте окрему закупівлю:

.. http:example:: multiple_lots_tutorial/tender-view.http
   :code:



Реєстрація пропозиції
---------------------

Статус закупівлі ``active.tendering`` дозволяє реєстрацію пропозицій.

Учасник може зареєструвати пропозицію для лота №1:

.. http:example:: multiple_lots_tutorial/bid-lot1.http
   :code:

Учасник може зареєструвати пропозиції для всіх лотів:

.. http:example:: multiple_lots_tutorial/bid-lot2.http
   :code:

Учасник повинен завантажити технічні та приватні документи пропозиції.

Закупівлю можна оновлювати протягом періоду ``active.tendering``. Всі пропозиції вважатимуться недійсними після оновлення закупівлі. Наприклад, зменшимо ціну лота до 400.

.. http:example:: multiple_lots_tutorial/tender-invalid-all-bids.http
   :code:

Це пропозиція учасника після оновлення закупівлі.

.. http:example:: multiple_lots_tutorial/bid-lot1-invalid-view.http
   :code:

Спочатку учасник повинен поновити свою пропозицію, навіть якщо подавав її лише для лота №1.

.. http:example:: multiple_lots_tutorial/bid-lot1-update-view.http
   :code:

Потім учасник повинен поновити пропозицію для лота №1.

.. http:example:: multiple_lots_tutorial/bid-lot2-update-view.http
   :code:


Кваліфікація пропозицій
-----------------------

Для процедури конкурентного діалогу необхідна кваліфікація значень пропозицій.

Переглянемо закупівлю: 

.. http:example:: multiple_lots_tutorial/tender-view-pre-qualification.http
   :code:

Переглянемо список кваліфікацій:

.. http:example:: multiple_lots_tutorial/qualifications-view.http
   :code:

Підтвердіть значення пропозиції через кваліфікаційні об’єкти:

.. http:example:: multiple_lots_tutorial/tender-activate-qualifications.http
   :code:


Замовник підтверджує кваліфікацію переходом до наступного статусу.

Перед схваленням рішення необхідно додати файл підпису до тендеру. Файл підпису повинен бути доданий до тендеру загалом. Якщо нема файлу підпису під час схвалення кваліфікації, ми побачимо помилку:

.. http:example:: multiple_lots_tutorial/pre-qualification-sign-doc-is-required.http
   :code:

Файд підпису повинен мати `documentType: evaluationReports` та `title: *.p7s`. Додамо такий документ:

.. http:example:: multiple_lots_tutorial/upload-evaluation-reports-doc.http
   :code:

Ще раз схвалимо кваліфікацію заявок:

.. http:example:: multiple_lots_tutorial/tender-view-pre-qualification-stand-still.http
   :code:

В цій процедурі є період блокування на 10 днів під час `qualificationPeriod`.

Другий етап
-----------

На другому етапі ми повині реєструвати нові пропозіції, але реєструвати можуть тільки учасники, які були допущени на першому етапі.

Спробуємо

.. http:example:: multiple_lots_tutorial/register_bad_bid.http
   :code:

Отримали помилку

Тепер, зареєструємо пропозицію постачальником, який був допущений на першому етапі на перший лот

.. http:example:: multiple_lots_tutorial/register_ok_bid.http
   :code:

Вдалося!

Тепер спробуємо зареєструємо на лот на який постачальник не був допущений.

.. http:example:: multiple_lots_tutorial/register_bad_not_allowed_lot.http
   :code:

Ми знову виявляємо помилку. Таким чином, ми можемо зробити висновок, що тільки користувач з першого етапу може зареєструвати ставку на другому етапі.
