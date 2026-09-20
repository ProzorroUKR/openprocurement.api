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
