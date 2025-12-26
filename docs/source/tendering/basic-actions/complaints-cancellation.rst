

Отримання інформації про скарги
===============================

Отримання інформації про скарги на скасування закупівлі
-------------------------------------------------------

Ви можете отримати список всіх скарг на скасування закупівлі:

.. http:example:: http/complaints/cancellation-complaints-list.http
   :code:

Або перевірити окрему скаргу:

.. http:example:: http/complaints/cancellation-complaint.http
   :code:


Подання скарги
==============

Якщо умови закупівлі сприятливі лише для одного постачальника або при будь-якому іншому серйозному порушенні, будь-який зареєстрований користувач можеподати скаргу на умови закупівлі, якщо скарга в статусі `active.tendering` чи тільки учасники закупівлі, якщо скарга у будь-яком іншому статусі.

Подання скарги на скасування закупівлі (з документами)
------------------------------------------------------

Створити скаргру на відміну закупівлі може будь-хто, якщо тендер в статусі `active.auction` або тільки учасники закупівлі в іншому статусі

Створіть чернетку скарги ``draft``:

.. http:example:: http/complaints/cancellation-complaint-submission.http
   :code:

При створенні скарги Користувач може додати одне або декілька Заперечень, що висуваються Скаржником в рамках скарги (objections). Заперечення можуть бути додані або відредаговані, коли скарга знаходиться в статусі `draft`. Детальніше дивитися: :ref:`Заперечення до скарг <complaint-objections>`

Потім завантажте документи:

.. http:example:: http/complaints/cancellation-complaint-submission-upload.http
   :code:

Подайте скаргу на скасування зікупівлі

.. http:example:: http/complaints/cancellation-complaint-complaint.http
   :code:

Подання скарги на скасування закупівлі (без документів)
-------------------------------------------------------

Ви можете подати скаргу, що не потребує додаткових документів:

.. http:example:: http-outdated/complaints/cancellation-complaint-submission-complaint.http
   :code:

Iнформація про оскарження скарги в суді
=======================================

Для скарги у статусах `invalid`, `satisfied`, `declined` та `resolved` власник тендеру або автор скарги мають можливість додати інформацію про оскарження скарги в суді.

Детальніше дивитися: :ref:`Iнформація про оскарження скарги в суді <complaint-appeals>`

Пояснення до скарги
===================

Пояснення до скарги - це певна текстова інформація та за потреби прикріплений файл/файли, що відносяться до певної скарги та можуть бути використані комісією АМКУ при її розгляді. Пояснення до скарги подаються суб'єктами з власної ініціативи, без запиту АМКУ. АМКУ не буде відповідати на такі пояснення, а лише розглядатиме їх.

Для скарги у статусах `pending` та `accepted` скаржник, що подав скаргу, або замовник закупівлі має можливість додати пояснення до скарги.

Пояснення можна додавати не пізніше ніж за 3 робочі дні до дати розгляду скарги (3 рд до reviewDate)

Кожне пояснення обов'язково повинно відноситись до одного із пунктів скарги (`complaints:objections`).

Скаржник, що подав скаргу, або замовник закупівлі можуть додати пояснення до скарги за допомогою функціоналу `posts`:

.. http:example:: http/complaints/cancellation-complaint-post-explanation.http
   :code:

Поле `recipient` заборонено для пояснень:

.. http:example:: http/complaints/cancellation-complaint-post-explanation-invalid.http
   :code:

Заборонено надавати відповідь до пояснення, передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/cancellation-complaint-post-explanation-answer-forbidden.http
   :code:


Вирішення скарги
================

Відхилення скарги на умови закупівлі
------------------------------------

.. http:example:: http/complaints/cancellation-complaint-reject.http
   :code:


Прийняття скарги на скасування закупівлі
----------------------------------------

.. http:example:: http/complaints/cancellation-complaint-accept.http
   :code:


Подання рішення по скарзі на скасування закупівлі
-------------------------------------------------

Орган, що розглядає скарги, завантажує документ з рішенням:

.. http:example:: http/complaints/cancellation-complaint-resolution-upload.http
   :code:

Який або вирішує скаргу:

.. http:example:: http/complaints/cancellation-complaint-resolve.http
   :code:

Або відхиляє:

.. http:example:: http/complaints/cancellation-complaint-decline.http
   :code:

Подання підтведження вирішення скарги
-------------------------------------

Для подання підтвердження вирішення скарги, скасування на скасування закупівлі повинно перебевати у статусі `unsuccessful`.

.. http:example:: http/complaints/cancellation-complaint-resolved.http
   :code:

Коли скарга на скасування закупівлі змінює статус на `resolved` вібувається перерахунок усіх періодів, що стосуються закупівлі за формулою:

.. code-block:: python

   period.endDate += complaint.tendererActionDate - cancellation.complaintPeriod.startDate

Відміна скарги на скасування закупівлі
======================================

Відміна не прийнятої скарги
---------------------------

.. http:example:: http/complaints/cancellation-complaint-reject.http
   :code:

Відміна прийнятої скарги рецензентом
------------------------------------

.. http:example:: http/complaints/cancellation-complaint-accepted-stopped.http
   :code:
