.. _competitiveordering_long_tutorial:

Туторіал (подовжений тендер)
============================

Конфігурація
------------

Набір можливих значень конфігурації:

.. csv-table::
   :file: csv/config-long.csv
   :header-rows: 1

Ви можете ознайомитись з деталями в секції :ref:`config`.

Створення тендеру
-----------------

Для тендеру `competitiveOrdering` замовник зазначає, що був попередній відбір учасників та вказує id agreement.

Використаємо `agreement` для прикладу:

.. http:example:: http/long/view-agreement-1-contract.http
   :code:

Ми можемо створити тендер, вказавши цей `agreement`:

.. http:example:: http/long/tender-post-attempt-json-data.http
   :code:

Також необхідно відредагувати дані `relatedLot` в `items`:

.. http:example:: http/long/tender-add-relatedLot-to-item.http
   :code:

Активація тендеру
-----------------

Спочатку нам потрібно додати вийняткові критерії до нашої закупівлі (:ref:`Про критерії ви можете дізнатися тут<criteria_operation>`)

.. http:example:: http/long/add-exclusion-criteria.http
   :code:

Спробуємо активувати тендер:

.. http:example:: http/long/tender-activating-insufficient-active-contracts-error.http
   :code:

Ми побачимо помилку, тому що в нас недостатньо активних контрактів в нашій угоді.

Список помилок пов'язаних з угодою, які можуть виникати при активації тендеру:

* Agreement not found in agreements
* Agreement status is not active
* Agreement has less than 3 active contracts
* tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)

Перед активацією тендера необхідно обов'язково додати файл підпису. Якщо такого документу нема, під час активації буде помилка:

.. http:example:: http/long/notice-document-required.http
   :code:

Файл підпису повинен мати `documentType: notice` та `title: *.p7s`. Додамо такий документ:

.. http:example:: http/long/add-notice-document.http
   :code:

Після того, як були додані ще активні контракти до нашої угоди та файл підпису, зробимо ще одну спробу активації тендеру:

.. http:example:: http/long/tender-activating.http
   :code:

Ми побачимо, що тендер був успішно активований:

Звернення
---------

Поки тендерна пропозиція має статус ``active.tendering``, а момент ``Tender.enquiryPeriod.endDate`` ще не настав, зацікавлені сторони можуть подавати звернення:

.. http:example:: http/long/ask-question.http
   :code:

Відмінність у зверненнях від :ref:`open` процедури це те, що в `competitiveOrdering` звернення щодо тендерної документації можуть подавати лише кваліфіковані учасники. Якщо якийсь інший автор спробує додати звернення, буде помилка:

.. http:example:: http/long/ask-question-invalid-author.http
   :code:


Закінчення періоду подання пропозицій
-------------------------------------

По закінченню періоду подання пропозицій (active.tendering) система знову перевіряє статус учасника у agreement. Якщо досі `аctive` - bid отримує `status:active`, якщо інший статус - пропозиція падає у статус `invalid`.

Припустимо, що на початку періоду `active.tendering` була подана пропозиція, в якій постачальний був кваліфікований в угоді, тому він успішно став учасником тендеру:

.. http:example:: http/long/register-third-bid.http
   :code:

Вже після цього цей постачальник в угоді був дискваліфікований під час періоду `active.tendering`.

Подивимося на статус нашої пропозицій після закінчення періоду `active.tendering`. Пропозиція, в якій постачальник був дискваліфікований в угоді, тепер має статус `invalid`:

.. http:example:: http/long/active-tendering-end-not-member-bid.http
   :code:


Підтвердження кваліфікації
--------------------------

Кваліфікаційна комісія може винести рішення по переможцю або відхилити award - перевести авард в `active` або `unsuccessful` статус.

Валідація значення полів відповідно до рішення під час винесення рішення:

* `qualified: True` - при переході award з `pending` в `active`

* `qualified: False` - при переході award з `pending` в `unsuccessful`

Так як тендер `competitiveOrdering` не має критеріїв статті 17, заборонено передавали поле `eligible` для авардів.

.. note::
    Подальші дії для тендеру `competitiveOrdering` такі ж самі як для :ref:`open`, ви можете дотримуватися відповідного туторіалу :ref:`open_tutorial`.
