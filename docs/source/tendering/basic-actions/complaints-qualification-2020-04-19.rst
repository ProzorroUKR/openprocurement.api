

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

Подання скарги
==============

Якщо кваліфікація сприятлива лише для одного постачальника або при будь-якому іншому серйозному порушенні, учасники можуть подати скаргу на кваліфікацію.

Подання скарги на кваліфікацію
------------------------------

Спочатку створіть скаргу. В POST запиті потрібно передати токен доступу одного з учасників, який вже подав пропозицію.

.. http:example:: http/complaints/qualification-complaint-submission.http
   :code:

При створенні скарги Користувач може додати одне або декілька Заперечень, що висуваються Скаржником в рамках скарги (objections). Заперечення можуть бути додані або відредаговані, коли скарга знаходиться в статусі `draft`. Детальніше дивитися: :ref:`Заперечення до скарг <complaint-objections>`

Цей крок не обов'язковий.Завантажте документи:

.. http:example:: http/complaints/qualification-complaint-submission-upload.http
   :code:

Подайте скаргу на кваліфікацію:

.. http:example:: http/complaints/qualification-complaint-complaint.http
   :code:


Запит до скарги
===============

Для скарги у статусах 'pending' та 'accepted' орган оскарження має можливість додати запит на уточнення до скарги.

Запит до скарги на кваліфікацію (до скаржника)
----------------------------------------------

Орган оскарження може надати запит до скаржника:

.. http:example:: http/complaints/qualification-complaint-post-reviewer-complaint-owner.http
   :code:

Скаржник має можливість надати відповідь на запит органу оскарження передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/qualification-complaint-post-complaint-owner.http
   :code:

Запит до скарги на кваліфікацію (до замовника)
----------------------------------------------

Орган оскарження може надати запит до замовника:

.. http:example:: http/complaints/qualification-complaint-post-reviewer-tender-owner.http
   :code:

Замовник має можливість надати відповідь на запит органу оскарження передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/qualification-complaint-post-tender-owner.http
   :code:

Подання документів до запиту до скарги на кваліфікацію
------------------------------------------------------

Документи до запиту до скарги мають бути додані до самої скарги з вказаними полями `documentOf: post` та `relatedItem` ідентифікатором самого запиту.

Документи до запиту до скарги можуть бути додані поки скарга має статус `pending` чи `accepted`.

Тільки автор запиту до скарги може додавати документ, який посилається на його запит. Спробуємо додати документи до запиту від замовника, від імені іншого автора (скаржника):

.. http:example:: http/complaints/qualification-complaint-post-documents-forbidden.http
   :code:

Додамо документи від імені замовника до його запиту:

.. http:example:: http/complaints/qualification-complaint-post-documents-tender-owner.http
   :code:


Iнформація про оскарження скарги в суді
=======================================

Для скарги у статусах `invalid`, `satisfied`, `declined` та `resolved` власник тендеру або автор скарги мають можливість додати інформацію про оскарження скарги в суді.

Детальніше дивитися: :ref:`Iнформація про оскарження скарги в суді <complaint-appeals>`

Пояснення до скарги
===================

Пояснення до скарги - це певна текстова інформація та за потреби прикріплений файл/файли, що відносяться до певної скарги та можуть бути використані комісією АМКУ при її розгляді. Пояснення до скарги подаються суб'єктами з власної ініціативи, без запиту АМКУ. АМКУ не буде відповідати на такі пояснення, а лише розглядатиме їх.

Для скарги у статусах `pending` та `accepted` скаржник, що подав скаргу, або замовник закупівлі має можливість додати пояснення до скарги.

Кожне пояснення обов'язково повинно відноситись до одного із пунктів скарги (`complaints:objections`).

Скаржник, що подав скаргу, або замовник закупівлі можуть додати пояснення до скарги за допомогою функціоналу `posts`:

.. http:example:: http/complaints/qualification-complaint-post-explanation.http
   :code:

Поле `recipient` заборонено для пояснень:

.. http:example:: http/complaints/qualification-complaint-post-explanation-invalid.http
   :code:

Заборонено надавати відповідь до пояснення, передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/qualification-complaint-post-explanation-answer-forbidden.http
   :code:


Вирішення скарги
================

Відхилення скарги на кваліфікацію
---------------------------------

.. http:example:: http/complaints/qualification-complaint-reject.http
   :code:


Прийняття скарги на кваліфікацію
--------------------------------

.. http:example:: http/complaints/qualification-complaint-accept.http
   :code:


Подання рішення по скарзі на кваліфікацію
-----------------------------------------

Орган оскарження завантажує документ з рішенням:

.. http:example:: http/complaints/qualification-complaint-resolution-upload.http
   :code:

Яке або вирішує скаргу:

.. http:example:: http/complaints/qualification-complaint-resolve.http
   :code:

Або відхиляє скаргу:

.. http:example:: http/complaints/qualification-complaint-decline.http
   :code:

Подання вирішення скарги
------------------------

.. http:example:: http/complaints/qualification-complaint-resolved.http
   :code:

Відміна скарги на кваліфікацію
==============================

Відміна чернетки скарги скаржником
----------------------------------

.. http:example:: http/complaints/qualification-complaint-mistaken.http
   :code:

Відміна прийнятої скарги рецензентом
------------------------------------

.. http:example:: http/complaints/qualification-complaint-accepted-stopped.http
   :code:
