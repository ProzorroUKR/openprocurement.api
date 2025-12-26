

Отримання інформації про звернення/скарги
=========================================

Отримання інформації про звернення/скарги на визначення переможця
-----------------------------------------------------------------

Ви можете отримати список всіх звернень/скарг на визначення переможця:

.. http:example:: http/complaints/award-complaints-list.http
   :code:

І перевірити окрему скаргу:

.. http:example:: http/complaints/award-complaint.http
   :code:

Подання звернення
=================

Якщо при визначенні переможця відбулось порушення чи була допущена помилка, то учасник закупівлі може подати звернення щодо результатів визначення переможця.

Подання звернення (з документами)
---------------------------------

Створіть звернення. В POST запиті потрібно передати токен доступу одного з учасників.

.. http:example:: http/complaints/award-claim-submission.http
   :code:

Потім завантажте документи:

.. http:example:: http/complaints/award-complaint-submission-upload.http
   :code:

Подайте звернення:

.. http:example:: http/complaints/award-complaint-claim.http
   :code:

Подання звернення (без документів)
----------------------------------

Ви можете подати звернення, що не потребує додаткових документів:

.. http:example:: http/complaints/award-complaint-submission-claim.http
   :code:

Відповідь на звернення
======================

Відповідь на вирішене звернення
-------------------------------

.. http:example:: http/complaints/award-complaint-answer.http
   :code:


Задовільнене звернення
======================

Рішення про задовільнення звернення
-----------------------------------

.. http:example:: http/complaints/award-complaint-satisfy.http
   :code:


Рішення про відхилення звернення
--------------------------------

.. http:example:: http/complaints/award-complaint-unsatisfy.http
   :code:
