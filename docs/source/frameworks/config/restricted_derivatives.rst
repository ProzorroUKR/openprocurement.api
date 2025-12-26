restrictedDerivatives
=====================

Створення фреймворку з обмеженим доступом
-----------------------------------------

Спочатку створимо фреймворк з обмеженим доступом з токеном майданчика. Для цього нам потрібно встановити ``restricted_derivatives`` поле в ``true`` в ``config`` розділі запиту на створення фреймворку.

.. http:example:: http/restricted/framework-create-broker.http
   :code:

Цей фреймворк видно всім в публічному API.

.. note::
    Для `ProcuringEntity` з kind `defense` поле ``restricted_derivatives`` буде встановлено в ``true`` автоматично.

Другий крок - перехід фреймворку в статус `active`:

.. http:example:: http/restricted/framework-activate-broker.http
   :code:

Створення та активація пропозицій з обмеженим доступом
------------------------------------------------------

Після активації фреймворку користувачі можуть зареєструвати свої пропозиції в період від `framework.period.startDate` до framework.period.endDate`.

Зареєструємо пропозицію:

.. http:example:: http/restricted/submission-register-broker.http
   :code:

Ви можете побачити, що поле ``restricted`` було встановлено в ``true`` в розділі ``config`` відповіді на створення пропозиції.

Далі активуємо пропозицію:

.. http:example:: http/restricted/submission-activate-broker.http
   :code:

Запит пропозицій з обмеженим доступом
-------------------------------------

Перевіримо пропозиції всіх учасників:

Анонімно
********

Створимо пропозицію використовуючи анонімний запит:

.. http:example:: http/restricted/submission-get-anonymous.http
   :code:

Бачимо що деякі її поля приховані.

Перевіримо фід пропозицій з анонімним запитом:

.. http:example:: http/restricted/submission-feed-anonymous.http
   :code:

Майданчик
*********

Але якщо ми зробимо запит з `broker` токеном майданчика , ми побачимо, що відповідні поля більше не приховані:

.. http:example:: http/restricted/submission-get-broker.http
   :code:

Перевіримо фід пропозицій для майданчика:

.. http:example:: http/restricted/submission-feed-broker.http
   :code:

Запит кваліфікацій з обмеженим доступом
---------------------------------------

Перевіримо кваліфікацію:

Анонімно
********

Переглнемо кваліфікацію з анонімним запитом:

.. http:example:: http/restricted/qualification-get-anonymous.http
   :code:

Бачимо що деякі її поля приховані.

Перевіримо фід кваліфікацій з анонімним запитом:

.. http:example:: http/restricted/qualification-feed-anonymous.http
   :code:

Майданчик
*********

Але якщо ми зробимо запит з `broker` токеном майданчика , ми побачимо, що відповідні поля більше не приховані:

.. http:example:: http/restricted/qualification-get-broker.http
   :code:

Перевіримо фід кваліфікацій для майданчика:

.. http:example:: http/restricted/submission-feed-broker.http
   :code:

Активуція кваліфікації з обмеженим доступом
-------------------------------------------

Перевіримо поточний фреймворк

.. http:example:: http/restricted/framework-with-agreement.http
   :code:

Активуємо кваліфікацію:

.. http:example:: http/restricted/qualification-activate-broker.http
   :code:

Ви можете побачити, що `agreementID` з'явився в поточному фреймворку, тому перевіримо цю угоду.

Запит угоди з обмеженим доступом
--------------------------------

Переглянемо угоду:

Анонімно
********

Переглянемо угоду використовуючи анонімний запит:

.. http:example:: http/restricted/agreement-get-anonymous.http
   :code:

Бачимо що деякі її поля приховані.

Перевіримо фід угод використовуючи анонімний запит:

.. http:example:: http/restricted/agreement-feed-anonymous.http
   :code:

Майданчик
*********

Але якщо ми зробимо запит з `broker` токеном майданчика , ми побачимо, що відповідні поля більше не приховані:

.. http:example:: http/restricted/agreement-get-broker.http
   :code:

Перевіримо фід угод для майданчика:

.. http:example:: http/restricted/agreement-feed-broker.http
   :code:

Правила маскування
------------------

.. note::
    Правила складаються з JSONPath виразів. Для отримання додаткової інформації читайте `JSONPath specification <https://goessner.net/articles/JsonPath/>`_.

Правила маскування пропозицій:

.. csv-table::
   :file: csv/restricted/submission-mask-mapping.csv
   :header-rows: 1

Rules for qualification masking:

.. csv-table::
   :file: csv/restricted/qualification-mask-mapping.csv
   :header-rows: 1

Правила маскування угод:

.. csv-table::
   :file: csv/restricted/agreement-mask-mapping.csv
   :header-rows: 1
