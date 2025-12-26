

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

Подання скарги
==============

Якщо тендерн вирішено з перевагою для певного постачальника або в будь-якій іншій життєздатній ситуації, учасники, які були прийняті до аукціону, можуть подати скаргу тендерної пропозиції.

Подання скарги на визначення переможця (з документами)
------------------------------------------------------

Спочатку створимо скаргу. В запиті потрібно передати токен доступу одного з учасників.

.. http:example:: http/complaints/award-complaint-submission.http
   :code:

Потім завантажте документи:
                           
.. http:example:: http/complaints/award-complaint-submission-upload.http
   :code:

І подамо скаргу на визначення переможця:
                                        
.. http:example:: http/complaints/award-complaint-complaint.http
   :code:

Подання скарги на визначення переможця (без документів)
-------------------------------------------------------

Ви можете подати скаргу, що не потребує додаткових документів:

.. http:example:: http-outdated/complaints/award-complaint-submission-complaint.http
   :code:

Запит до скарги
===============

Для скарги у статусах `pending` та `accepted` орган оскарження має можливість додати запит на уточнення до скарги.

Запит до скарги на умови закупівлі (до скаржника)
-------------------------------------------------

Орган оскарження може надати запит до скаржника:

.. http:example:: http/complaints/award-complaint-post-reviewer-complaint-owner.http
   :code:

Скаржник має можливість надати відповідь на запит органу оскарження передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/award-complaint-post-complaint-owner.http
   :code:

Запит до скарги на умови закупівлі (до замовника)
-------------------------------------------------

Орган оскарження може надати запит до замовника:

.. http:example:: http/complaints/award-complaint-post-reviewer-tender-owner.http
   :code:

Замовник має можливість надати відповідь на запит органу оскарження передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/award-complaint-post-tender-owner.http
   :code:

Пояснення до скарги
===================

Пояснення до скарги - це певна текстова інформація та за потреби прикріплений файл/файли, що відносяться до певної скарги та можуть бути використані комісією АМКУ при її розгляді. Пояснення до скарги подаються суб'єктами з власної ініціативи, без запиту АМКУ. АМКУ не буде відповідати на такі пояснення, а лише розглядатиме їх.

Для скарги у статусах `pending` та `accepted` скаржник, що подав скаргу, або замовник закупівлі має можливість додати пояснення до скарги.

Пояснення можна додавати не пізніше ніж за 3 робочі дні до дати розгляду скарги (3 рд до reviewDate)

Кожне пояснення обов'язково повинно відноситись до одного із пунктів скарги (`complaints:objections`).

Скаржник, що подав скаргу, або замовник закупівлі можуть додати пояснення до скарги за допомогою функціоналу `posts`:

.. http:example:: http/complaints/award-complaint-post-explanation.http
   :code:

Поле `recipient` заборонено для пояснень:

.. http:example:: http/complaints/award-complaint-post-explanation-invalid.http
   :code:

Заборонено надавати відповідь до пояснення, передавши поле `id` запиту у полі `relatedPost`:

.. http:example:: http/complaints/award-complaint-post-explanation-answer-forbidden.http
   :code:

Вирішення скарги
================

Відхилення скарги на визначення переможця
-----------------------------------------

.. http:example:: http/complaints/award-complaint-reject.http
   :code:


Прийняття скарги на визначення переможця
----------------------------------------

.. http:example:: http/complaints/award-complaint-accept.http
   :code:


Подання рішення по скарзі на визначення переможця
-------------------------------------------------

Орган, що розглядає скарги, завантажує документ з рішенням:

.. http:example:: http/complaints/award-complaint-resolution-upload.http
   :code:

Яке або вирішує скаргу:

.. http:example:: http/complaints/award-complaint-resolve.http
   :code:

Або відхиляє:

.. http:example:: http/complaints/award-complaint-decline.http
   :code:

Виправлення проблем
-------------------

Якщо скарга на визначення переможця була задоволена органом оскарження, то замовник повинен виправити допущені порушення.

Одним з можливих рішень є відміна результатів визначення переможця (`award`):


.. http:example:: http/complaints/award-complaint-satisfied-resolving.http
   :code:

При відміні результатів визначення переможця система генерує новий `award`. Шлях до нього передається в `Location` заголовку відповіді.

Подання підтвердження вирішення скарги
--------------------------------------
Якщо скаргу вирішено і порушення усунуто, то замовник подає підтвердження вирішення.

.. http:example:: http/complaints/award-complaint-resolved.http
   :code:

Подання скарги на нове визначення переможця
-------------------------------------------

.. http:example:: http/complaints/award-complaint-submit.http
   :code:

Відміна скарги на визначення переможця
======================================

Відміна скарги в статусі `pending` рецензентом
----------------------------------------------

.. http:example:: http-outdated/complaints/award-complaint-mistaken.http
   :code:

Відміна прийнятої скарги скаржником
-----------------------------------

.. http:example:: http-outdated/complaints/award-complaint-accepted-stopping.http
   :code:

.. http:example:: http-outdated/complaints/award-complaint-stopping-stopped.http
   :code:

Відміна прийнятої скарги рецензентом
------------------------------------

.. http:example:: http/complaints/award-complaint-accepted-stopped.http
   :code:
