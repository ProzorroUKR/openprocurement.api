
.. _agreement_framework_tutorial:

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

Створення реєстру
-----------------

Припустимо, що є кваліфікація, заявка та рішення по заявці в статусах ``active``. Коли заявка в стаусі `active` і ви оновлюєте рішення по заявці до `active` статусу система **автоматично** створює реєстр(з кваліфікації) з контрактом(з рішення по заявці).

Отримання реєстру
-----------------

Перевіримо нашу кваліфікацію:

.. http:example:: http/example-framework.http
   :code:

В нашій кваліфікації ви можете знайти поле `agreementID` в якому зберегіється ідентифікатор пов'язоного реєстру. Тепер ми можемо отримати на реєстр:

.. http:example:: http/agreement-view.http
   :code:


Зміна реєстру
-------------

Всі операцї над реєстром може виконувати лише `framework_owner`. Лише одна річ, яку може робити `framework_owner` це додавати/змінювати майлстони до контракту.

Контракт - об'єкт що зберігає інформацію про учасника.

Майлстон - це історія контраку.

Бан контракту
~~~~~~~~~~~~~

Для того щоб забанити контракт, потрібно лише створити майлстон зі статусом `ban`:

.. http:example:: http/milestone-ban-post.http
   :code:

You can see that contract status was automatically changed to `suspended`:

.. http:example:: http/agreement-view-contract-suspended.http
   :code:

After `dueDate` date of milestone, contract will be automatically set back to `active` status.

.. http:example:: http/agreement-view-contract-active.http
   :code:

Contract disqualify
~~~~~~~~~~~~~~~~~~~

You can see that contract was automatically created with `activation` milestone.

Field `dueDate` was automatically set with `period.endDate` date. On that date milestone will be automatically set to `met` status, and contract will switched status to `terminated`.

When you want to manually disqualify contract, you need to manually set `activation` milestone status to `met`:

.. http:example:: http/milestone-activation-patch.http
   :code:

Now you can see that contract status was changed to `terminated`:

.. http:example:: http/agreement-view-contract-terminated.http
   :code:

Finishing agreement
~~~~~~~~~~~~~~~~~~~

Lets wait for `period.endDate` date and see what will happen:

.. http:example:: http/agreement-view-terminated.http
   :code:

You can see that `activation` milestone was automatically set to `met` status, contract status was changed to `terminated` and agreement status was changed to `terminated`.
