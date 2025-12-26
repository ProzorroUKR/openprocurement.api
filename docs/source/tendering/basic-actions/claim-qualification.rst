

Отримання інформації по вимогах/скаргах
=======================================

Отримання інформації по вимогах/скаргах на кваліфікацію
-------------------------------------------------------

Ви можете отримати список всіх вимог/скарг на кваліфікацію:

.. http:example:: http/complaints/qualification-complaints-list.http
   :code:

І перевірити окрему скаргу:

.. http:example:: http/complaints/qualification-complaint.http
   :code:

Подання вимоги
==============

Якщо під час етапу кваліфікації відбулось порушення чи була допущена помилка, то учасник закупівлі може подати вимогу про виправлення кваліфікації.

Подання вимоги про виправлення кваліфікації (з документами)
-----------------------------------------------------------

Спочатку створіть вимогу. В POST запиті потрібно передати токен доступу одного з учасників.

.. http:example:: http/complaints/qualification-claim-submission.http
   :code:

Потім завантажте необхідні документи:

.. http:example:: http/complaints/qualification-claim-submission-upload.http
   :code:

Подайте вимогу про виправлення кваліфікації:

.. http:example:: http/complaints/qualification-complaint-claim.http
   :code:

Подання вимоги про виправлення кваліфікації (без документів)
------------------------------------------------------------

Ви можете подати вимогу, що не потребує додаткових документів:

.. http:example:: http/complaints/qualification-complaint-submission-claim.http
   :code:


Відповідь на вимогу
===================

Відповідь на вирішену вимогу
----------------------------

.. http:example:: http/complaints/qualification-complaint-answer.http
   :code:


Задовільнена вимога
===================

Рішення про задовільнення вимоги
--------------------------------

.. http:example:: http/complaints/qualification-complaint-satisfy.http
   :code:


Рішення про відхилення вимоги
-----------------------------

.. http:example:: http/complaints/qualification-complaint-unsatisfy.http
   :code:
