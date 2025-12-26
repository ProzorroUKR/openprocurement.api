.. _violation_reports_tutorial:

Violation Reports (Звернення про порушення) Туторіал
====================================================


Опублікувати звіт про порушення
-------------------------------

Ви створюєте звіт з договору. Документи можна публікувати разом з даними.

.. http:example:: http/01-00-post-report-draft.http
   :code:

У стані `draft` звіт можна змінити

.. http:example:: http/01-01-patch-report-draft.http
   :code:


Ви можете видалити документ

.. http:example:: http/01-02-delete-document.http
   :code:


Можна опублікувати новий

.. http:example:: http/01-03-post-details-document.http
   :code:


Або ви можете оновити версію документа за допомогою методу PUT

.. http:example:: http/01-04-put-report-document-evidence.http
   :code:

Деталі документа оновлення можна змінити за допомогою методу PATCH

.. http:example:: http/01-05-patch-report-document-evidence.http
   :code:


Перед публікацією необхідно додати документ з підписом

.. http:example:: http/01-06-post-report-draft-signature.http
   :code:


Тепер ви можете опублікувати свій звіт про порушення, змінивши його статус

.. http:example:: http/01-07-publish-report-draft.http
   :code:


Див. `defendantPeriod`, що обмежує періоди публікації відповіді. Рішення можна опублікувати після закінчення періоду.


Опублікувати заяву відповідача
------------------------------
Опублікувати `draft` заяви

.. http:example:: http/02-01-put-defendant-statement.http
   :code:


Поки неактивний, ви можете його оновити

.. http:example:: http/02-02-update-defendant-statement.http
   :code:

Ви можете видалити документ

.. http:example:: http/02-03-delete-document.http
   :code:


Можна опублікувати новий

.. http:example:: http/02-04-post-defendant-document.http
   :code:


І оновити докази

.. http:example:: http/02-05-put-defendant-statement-evidence.http
   :code:


Змінити описи документів

.. http:example:: http/02-06-patch-defendant-statement-evidence.http
   :code:


Перед публікацією потрібно додати документ із підписом


.. http:example:: http/02-07-post-defendant-statement-signature.http
   :code:


Потім опублікуйте заяву, щоб вона з’явилася у стрічці змін

.. http:example:: http/02-08-publish-defendant-statement.http
   :code:


Опублікуйте рішення
-------------------

Створіть рішення у статусі `draft`

.. http:example:: http/03-01-create-decision.http
   :code:


Потрібно додати документ із підписом

.. http:example:: http/03-02-post-decision-signature.http
   :code:


Поки рішення у статусі `draft`, ви можете змінювати його


.. http:example:: http/03-03-change-decision.http
   :code:


Ви можете видалити документ

.. http:example:: http/03-04-delete-document.http
   :code:


Можна опублікувати новий

.. http:example:: http/03-05-post-decision-document.http
   :code:


Перед публікацією потрібно оновити підпис

.. http:example:: http/03-06-put-decision-signature.http
   :code:


Опублікуйте рішення

.. http:example:: http/03-07-publish-decision.http
   :code:


Перегляньте об’єкт результату звіту про порушення
-------------------------------------------------

.. http:example:: http/04-01-get-violation-report.http
   :code:


Поле `status` звіту про порушення тепер залежить від статусу рішення.


Оновлення звітів про порушення у стрічці змін
---------------------------------------------

Звіти про порушення з’являються у своїй стрічці змін, коли отримують публічні зміни.

Це такі:
  1. violationReport опубліковано
  2. defendantStatement опубліковано
  3. decision опубліковано


.. http:example:: http/05-01-feed.http
   :code:


Обробляйте об’єкти в `data` та переходьте за `next_page`

.. http:example:: http/05-02-feed-empty.http
   :code:

Коли `data` буде порожнім, призупиніть виконання скрипта на деякий час і перевірте цю саму сторінку пізніше.
