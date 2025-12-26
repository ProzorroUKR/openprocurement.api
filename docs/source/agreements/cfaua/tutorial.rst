.. _agreement_cfaua_tutorial:

Туторіал
========

Базові правила
--------------

Подивимось як працює точка входу `/agreements`:

.. http:example:: http/agreements-listing-0.http
   :code:

При виклику видає пустий набір.

Угода автоматично переноситься з модуля тендера.


.. index:: Agreements

Створення угоди
---------------

Припустимо, що ми провели тендер, який зараз є в статусі ``complete``. Після завершення тендера, угода, яка була створена в модулі тендера, переноситься у модуль угод **автоматично**.

*Майданчики (eMalls) не можуть створити угоди в модулі угод.*

Отримання угоди
---------------

Угода в модулі тендера

.. http:example:: http/example_agreement.http
   :code:

*Ідентифікатор угоди є тим самим і в модулі тендера, і в модулі угод.*

Звернемося до URL-адреси створеного об'єкта в модулі угод:

.. http:example:: http/agreement-view.http
   :code:

Отримання доступу
-----------------

Для того, щоб отримати права для редагування угоди в майбутньому, вам потрібно виконати ``PATCH: /agreements/{id}/credentials?acc_token={tender_token}`` з ключами майданчика до API, яким був згенерований тендер.

У ``PATCH: /agreements/{id}/credentials?acc_token={tender_token}``:

* ``id`` - ідентифікатор угоди,

* ``tender_token`` - це токен тендера (використовується для генерації токена угоди).

Відповідь міститиме ``access.token`` для угоди, який можна використовувати для майбутнього редагування угоди.

.. http:example:: http/agreement-credentials.http
   :code:

Подивимось на угоди.

.. http:example:: http/agreements-listing-1.http
   :code:


Бачимо внутрішні `id` угоди, який може бути використаний для побудови повної URL-адреси за допомогою додавання `http://api-sandbox.openprocurement.org/api/0/agreements/`, а також дату `dateModified`.


Редагування угоди
-----------------


**Основні умови договору** можуть бути модифіковані поданням нових об'єктів `change` у контейнер `Agreement.changes`. `Change` може бути таких типів: :ref:`ChangeTaxRate`, :ref:`ChangeItemPriceVariation`, :ref:`ChangePartyWithdrawal` або :ref:`ChangeThirdParty`

Усі об'єкти `changes` обробляються точкою входу `/agreement/{id}/changes`.

Подання зміни
~~~~~~~~~~~~~

Додамо новий `change` до угоди:

.. http:example:: http/add-agreement-change.http
   :code:

Візьміть до уваги, потрібно заповнити обов'язкове поле ``rationaleType``.

Подивимось на `change`:

.. http:example:: http/view-agreement-change.http
   :code:

`Change` може бути модифікований, поки об'єкт в статусі ``pending``:

.. http:example:: http/patch-agreement-change.http
   :code:

Завантаження документів до змін
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Документ може бути доданий тільки тоді, коли `change` в статусі ``pending``.

Документи додаються в два етапи:

* завантажте документ

.. http:example:: http/add-agreement-change-document.http
   :code:

* налаштуйте властивості документу ``"documentOf": "change"`` і ``"relatedItem": "{change.id}"`` для того, щоб підв'язати заватажений документ до об'єкту `change`:

.. http:example:: http/set-document-of-change.http
   :code:

Оновлення властивостей угоди
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Тепер можете оновити властивості угоди, які належать зміні.

.. http:example:: http/add-agreement-change-modification.http
   :code:

Є можливість змінювати кожен `factor` в `modifications` у випадку декількох :ref:`Item`.

Попередній перегляд угоди
~~~~~~~~~~~~~~~~~~~~~~~~~

Також, поки `change` в статусі ``pending``, можна бачити угоду, оскільки зміни будуть застосовані. Необхідно використати ``GET: /agreements/{id}/preview?acc_token={agreement_token}``.

.. http:example:: http/agreement_preview.http
   :code:

Як бачимо, `value.amount` на `unitPrices` об'єкту `contracts` змінюється після прийняття змін. Тож, якщо ці `зміни` - це те, що вам потрібно, то ви можете подати об'єкт `change`.

Застосування зміни
~~~~~~~~~~~~~~~~~~

`Change` може бути застосована після переходу в статус ``active``.

Для того, щоб застосувати статус ``active``, має бути налаштоване поле `dateSigned`.

Після цього `change` не можна більше модифікувати.

.. http:example:: http/apply-agreement-change.http
   :code:

Валідація поля `dateSigned`:

* для першої `change` в угоді, дата повинна бути після `agreement.dateSigned`;

* для всіх наступних об'єктів `change`, дата повинна бути після попередньої `change.dateSigned`.

Подивимось на всі зміни:

.. http:example:: http/view-all-agreement-changes.http
   :code:

Всі зміни також перераховані у view угоди.

.. http:example:: http/view-agreement.http
   :code:

Завантаження документів
-----------------------

Замовник може завантажити PDF-файли в створену угоду. Завантаження повинне слідувати правилам завантаження.

.. http:example:: http/upload-agreement-document.http
   :code:

Код відповіді 201 Created та заголовок Location підтверджують, що документ було додано. Додатково можна запитати точку входу API колекції `documents` для підтвердження дії:

.. http:example:: http/agreement-documents.http
   :code:

І знову можна підтвердити, що два документи завантажені.

.. http:example:: http/upload-agreement-document-2.http
   :code:

У випадку помилки, можна заново завантажити документ поверх старої версії:

.. http:example:: http/upload-agreement-document-3.http
   :code:

І можна побачити, що цей документ переважає оригінальну версію:

.. http:example:: http/get-agreement-document-3.http
   :code:


.. index:: Enquiries, Question, Answer


Завершення угоди
----------------

Угода може бути завершена переходом в статус ``terminated``. Давайте виконаємо ці дії одним запитом:

.. http:example:: http/agreement-termination.http
   :code:

Якщо угода неуспішна, причини припинення угоди повинні бути вказані в полі ``terminationDetails``.

Будь-які майбутні зміни в угоді не дозволяються.


Можливо, буде корисно побачити актуальні вимоги: `Сценарії ручного тестування для III рівня акредитації <https://docs.google.com/spreadsheets/d/1-AT2RjbnSFAP75x6YNDvhKeN2Cy3tMlG6kb0tt6FScs/edit#gid=0>`_ і `Сценарії ручного тестування для IV рівня акредитації <https://docs.google.com/spreadsheets/d/1-93kcQ2EeuUU08aqPMDwMeAjnG2SGnEEh5RtjHWOlOY/edit#gid=0>`_.
