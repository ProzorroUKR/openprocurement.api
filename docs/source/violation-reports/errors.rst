.. _violation_reports_errors:

Помилки API звітів про порушення
================================


Звіт про порушення у статусі `draft`
------------------------------------

Заборонено публікувати одразу опубліковані звіти  про порушення

.. http:example:: http/errors/00-01-post-pending-fail.http
    :code:


Спроба змінити звіт про порушення, додаючи зайві поля, має завершуватися помилкою.

.. http:example:: http/errors/01-05-patch-report-extra.http
   :code:


Зміна звіту про порушення без внесення змін має бути успішною, а значення dateModified має залишатися таким самим.

.. http:example:: http/errors/01-06-patch-report-no-changes.http
   :code:



DefendantStatement і Decision у статусі `draft`
-----------------------------------------------

Якщо звіт про порушення має статус `draft`, він ще не є публічним.

.. http:example:: http/errors/01-00-get-report.http
   :code:

Спроба опублікувати заяву відповідача має завершуватися помилкою.

.. http:example:: http/errors/01-01-put-defendant-statement.http
   :code:


Спроба додати документ заяви відповідача також має завершуватися помилкою.

.. http:example:: http/errors/01-01-put-defendant-statement.http
   :code:


Спроба опублікувати рішення має завершуватися помилкою.

.. http:example:: http/errors/01-03-put-decision.http
   :code:


Спроба додати документ рішення також має завершуватися помилкою.

.. http:example:: http/errors/01-04-post-decision-document.http
   :code:
