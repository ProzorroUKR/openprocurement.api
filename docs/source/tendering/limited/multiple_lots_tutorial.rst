.. _limited_mulitlot_tutorial:

Туторіал для багатолотової закупівлі
====================================


Створення закупівлі
-------------------

Створимо закупівлю:

.. http:example:: http/multiple_lots_tutorial/tender-post-attempt-json-data.http
   :code:

Тепер ми бачимо, що новий об’єкт було створено. Код відповіді - `201`, заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `active.tendering`.

Закупівля може складатись із декількох лотів. Можна створити лот таким чином:

.. http:example:: http/multiple_lots_tutorial/tender-add-lot.http
   :code:

Потрібно оновити дані пов’язані із залежністю на лот:

.. http:example:: http/multiple_lots_tutorial/tender-add-relatedLot-to-item.http
   :code:

Перегляньте список закупівель:

.. http:example:: http/multiple_lots_tutorial/tender-listing-no-auth.http
   :code:

або перегляньте окрему закупівлю:

.. http:example:: http/multiple_lots_tutorial/tender-view.http
   :code:


Ціна за одиницю в предметі закупівлі
------------------------------------

Правила для `items.unit.value` описані в розділі :ref:`limited_items_unit_value`.
В багатолотовій закупівлі сума добутків `item.quantity * item.unit.value.amount` рахується окремо в межах кожного лота
і звіряється з `value.amount` того лота, до якого предмети закупівлі прив'язані через `relatedLot`.

Створимо закупівлю з двома лотами, де сума по предметах закупівлі кожного лота дорівнює вартості цього лота
(`5 * 60000` для лота №1 та `2 * 100000` для лота №2):

.. http:example:: http/multiple_lots_tutorial/tender-post-attempt-json-data-unit-value.http
   :code:

Лоти перевіряються незалежно один від одного, тому зменшення ціни за одиницю в лоті №1 не можна компенсувати збільшенням ціни в лоті №2:

.. http:example:: http/multiple_lots_tutorial/tender-patch-items-unit-value-invalid.http
   :code:

Змінимо ціну за одиницю та кількість так, щоб сума по лоту №1 і далі дорівнювала його вартості:

.. http:example:: http/multiple_lots_tutorial/tender-patch-items-unit-value.http
   :code:


Визначення переможця
--------------------

Спосіб додавання інформації про постачальника однаковий для всіх процедур.

Додавання інформації про постачальника для лота №1:

.. http:example:: http/multiple_lots_tutorial/tender-award.http
   :code:

Підтвердження визначення переможця:

.. http:example:: http/multiple_lots_tutorial/tender-award-approve.http
   :code:

Різниця між початковою (``startDate``) та кінцевою (``endDate``) датою запису ``complaintPeriod`` для **переговорної** процедури становить 5 днів та 3 днів для **переговорної процедури за нагальною потребою**
