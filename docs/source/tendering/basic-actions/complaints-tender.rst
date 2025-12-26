

Отримання інформації про вимоги/скарги
======================================

Отримання інформації про вимоги/скарги на умови закупівлі
---------------------------------------------------------

Ви можете отримати список всіх вимог/скарг на умови закупівлі:

.. http:example:: http/complaints/complaints-list.http
   :code:

Або перевірити окрему скаргу чи вимогу:

.. http:example:: http/complaints/complaint.http
   :code:


Подання скарги
==============

Якщо умови закупівлі сприятливі лише для одного постачальника або при будь-якому іншому серйозному порушенні, будь-який зареєстрований користувач може подати скаргу на умови закупівлі.


Подання скарги на умови закупівлі (з документами)
-------------------------------------------------

Створіть чернетку скарги ``draft``:

.. http:example:: http/complaints/complaint-submission.http
   :code:

Потім завантажте документи:
                           
.. http:example:: http/complaints/complaint-submission-upload.http
   :code:

Подайте скаргу на умови закупівлі:
                                  
.. http:example:: http/complaints/complaint-complaint.http
   :code:

Подання скарги на умови закупівлі (без документів)
--------------------------------------------------

Ви можете подати скаргу, що не потребує додаткових документів:

.. http:example:: http-outdated/complaints/complaint-submission-complaint.http
   :code:

Запит до скарги
===============

Для скарги у статусах 'pending' та 'accepted' орган оскарження має можливість додати запит на уточнення до скарги.

Запит до скарги на умови закупівлі (до скаржника)
-------------------------------------------------

Орган оскарження може надати запит до скаржника:

.. http:example:: http/complaints/complaint-post-reviewer-complaint-owner.http
   :code:

Скаржник має можливість надати відповідь на запит органу оскарження передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/complaint-post-complaint-owner.http
   :code:

Запит до скарги на умови закупівлі (до замовника)
-------------------------------------------------

Орган оскарження може надати запит до замовника:

.. http:example:: http/complaints/complaint-post-reviewer-tender-owner.http
   :code:

Замовник має можливість надати відповідь на запит органу оскарження передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/complaint-post-tender-owner.http
   :code:

Пояснення до скарги
===================

Пояснення до скарги - це певна текстова інформація та за потреби прикріплений файл/файли, що відносяться до певної скарги та можуть бути використані комісією АМКУ при її розгляді. Пояснення до скарги подаються суб'єктами з власної ініціативи, без запиту АМКУ. АМКУ не буде відповідати на такі пояснення, а лише розглядатиме їх.

Для скарги у статусах `pending` та `accepted` скаржник, що подав скаргу, або замовник закупівлі має можливість додати пояснення до скарги.

Пояснення можна додавати не пізніше ніж за 3 робочі дні до дати розгляду скарги (3 рд до reviewDate)

Кожне пояснення обов'язково повинно відноситись до одного із пунктів скарги (`complaints:objections`).

Скаржник, що подав скаргу, або замовник закупівлі можуть додати пояснення до скарги за допомогою функціоналу `posts`:

.. http:example:: http/complaints/complaint-post-explanation.http
   :code:

Поле `recipient` заборонено для пояснень:

.. http:example:: http/complaints/complaint-post-explanation-invalid.http
   :code:

Заборонено надавати відповідь до пояснення, передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/complaint-post-explanation-answer-forbidden.http
   :code:


Вирішення скарги
================

Відхилення скарги на умови закупівлі
------------------------------------

.. http:example:: http/complaints/complaint-reject.http
   :code:


Прийняття скарги на умови закупівлі
-----------------------------------

.. http:example:: http/complaints/complaint-accept.http
   :code:


Подання рішення по скарзі на умови закупівлі
--------------------------------------------

Орган, що розглядає скарги, завантажує документ з рішенням:

.. http:example:: http/complaints/complaint-resolution-upload.http
   :code:

Який або вирішує скаргу:

.. http:example:: http/complaints/complaint-resolve.http
   :code:

Або відхиляє:

.. http:example:: http/complaints/complaint-decline.http
   :code:

Подання підтведження вирішення скарги
-------------------------------------

.. http:example:: http/complaints/complaint-resolved.http
   :code:

Відміна скарги на умови закупівлі
=================================

Відміна скарги в статусі `pending` рецензентом
----------------------------------------------

.. http:example:: http-outdated/complaints/complaint-mistaken.http
   :code:

Відміна прийнятої скарги скаржником
-----------------------------------

.. http:example:: http-outdated/complaints/complaint-accepted-stopping.http
   :code:

.. http:example:: http-outdated/complaints/complaint-stopping-stopped.http
   :code:

Відміна прийнятої скарги рецензентом
------------------------------------

.. http:example:: http/complaints/complaint-accepted-stopped.http
   :code:
