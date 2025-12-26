

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


Подання скарги на умови закупівлі
---------------------------------

Створіть чернетку скарги ``draft``:

.. http:example:: http/complaints/complaint-submission.http
   :code:

Цей крок не обов'язковий.Завантажте документи:

.. http:example:: http/complaints/complaint-submission-upload.http
   :code:

Подайте скаргу на умови закупівлі:

.. http:example:: http/complaints/complaint-complaint.http
   :code:


.. _complaint-objections:

Заперечення до скарги
=====================

При створенні скарги Користувач може додати одне або декілька Заперечень, що висуваються Скаржником в рамках скарги (objections):

.. http:example:: http/complaints/complaint-objections-submission.http
   :code:

Заперечення можуть бути додані або відредаговані, коли скарга знаходиться в статусі `draft`.

Для кожного Заперечення Скаржник обов'язково вказує одне або декілька Обгрунтуваннь (arguments). В іншому випадку буде помилка:

.. http:example:: http/complaints/complaint-objections-invalid-arguments.http
   :code:

Для кожного Обгрунтування Скаржник може вказати один або декілька Доказів (evidences). Докази можуть бути пустими:

.. http:example:: http/complaints/complaint-objections-empty-evidences.http
   :code:

Під час додавання Доказу, Користувач має вказати id відносного документу. Цей документ має попередньо бути завантаженим до скарги. Додамо документ до скарги:

.. http:example:: http/complaints/complaint-document-upload.http
   :code:

Після цього Користувач може вказати relatedDocument в Доказі:

.. http:example:: http/complaints/complaint-objections-evidences-with-document.http
   :code:

Також є можливість подати скаргу одним запитом одразу з завантаженим документом, який можна вказати в Доказі як `relatedDocument`:

.. http:example:: http/complaints/complaint-objections-with-document-one-action.http
   :code:

Для кожного Заперечення Скаржник обов'язково вказує одну або декілька Вимог (requestedRemedies). В іншому випадку буде помилка:

.. http:example:: http/complaints/complaint-objections-invalid-requested-remedies.http
   :code:


.. _complaint-appeals:

Iнформація про оскарження скарги в суді
=======================================

Після винесення рішення органом оскарження (АМКУ) по скарзі, замовник або учасник може оскаржити таке рішення в суді та опублікувати інформацію про це в системі:

.. http:example:: http/complaints/complaint-appeal-submission.http
   :code:

Iнформація про оскарження скарги в суді може бути додана або відредагована, коли скарга знаходиться в одному зі статусів:

    * `invalid`
    * `satisfied`
    * `declined`
    * `resolved`

Якщо інформація про оскарження скарги в суді буде додана на якомусь іншому статусі скарги, ми побачимо помилку:

.. http:example:: http/complaints/complaint-appeal-invalid-status.http
   :code:

До однієї скарги може бути опубліковано більше одного об’єкту `appeal` як учасниками так і замовником. Додамо ще одну апеляцію до скарги замовником:

.. http:example:: http/complaints/complaint-appeal-submission-by-customer.http
   :code:

Після публікації інформації про оскарження скарги в суді (`appeal`) можна додати інформацію про відкриття провадження (`proceeding`).

Інформація про оскарження скарги в суді та інформація про впровадження - це окремі дії, які виконуються користувачем поступово та може бути здійснено з проміжком у часі:

.. http:example:: http/complaints/complaint-appeal-proceeding-submission.http
   :code:

До кожного об’єкту `appeal` може бути опубліковано лише один об’єкт `proceeding`:

.. http:example:: http/complaints/complaint-appeal-proceeding-duplicate.http
   :code:

Після додавання інформації про оскарження скарги в суді та інформації про впровадження, необхідно накласти підпис. Документ можна додати через окремий ендпоінт:

.. http:example:: http/complaints/complaint-appeal-documents-submission.http
   :code:

Подивимося на скаргу з опублікованою інформацією про оскарження скарги в суді:

.. http:example:: http/complaints/complaint-appeal-get.http
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

Подання документів до запиту до скарги на умови закупівлі
---------------------------------------------------------

Документи до запиту до скарги мають бути додані до самої скарги з вказаними полями `documentOf: post` та `relatedItem` ідентифікатором самого запиту.

Документи до запиту до скарги можуть бути додані поки скарга має статус `pending` чи `accepted`.

Тільки автор запиту до скарги може додавати документ, який посилається на його запит. Спробуємо додати документи до запиту від замовника, від імені іншого автора (скаржника):

.. http:example:: http/complaints/complaint-post-documents-forbidden.http
   :code:

Додамо документи від імені замовника до його запиту:

.. http:example:: http/complaints/complaint-post-documents-tender-owner.http
   :code:


Пояснення до скарги
===================

Пояснення до скарги - це певна текстова інформація та за потреби прикріплений файл/файли, що відносяться до певної скарги та можуть бути використані комісією АМКУ при її розгляді. Пояснення до скарги подаються суб'єктами з власної ініціативи, без запиту АМКУ. АМКУ не буде відповідати на такі пояснення, а лише розглядатиме їх.

Для скарги у статусах `pending` та `accepted` скаржник, що подав скаргу, або замовник закупівлі має можливість додати пояснення до скарги.

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

Відміна чернетки скарги скаржником
----------------------------------

.. http:example:: http/complaints/complaint-mistaken.http
   :code:

Відміна прийнятої скарги рецензентом
------------------------------------

.. http:example:: http/complaints/complaint-accepted-stopped.http
   :code:
