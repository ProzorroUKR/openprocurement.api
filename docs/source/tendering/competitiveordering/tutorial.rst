.. _competitiveordering_tutorial:

Tutorial
========

Configuration
-------------

The set of possible configuration values:

.. csv-table::
   :file: csv/config.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

The set of possible `procuringEntity.kind` values for `competitiveOrdering`
---------------------------------------------------------------------------

.. csv-table::
   :file: csv/kind.csv
   :header-rows: 1

Відбір
------
У відборі (1 етап) замовник самостійно зазначає
чи він буде деталізувати предмети закупівлі на першому етапі,
чи він це зробить безпосереньо в закупівлі.

Замовник на етапі створення відбору може вибрати, чи буде він деталізувати предмети закупівлі на першому етапі, за допомогою встановлення конфігурації процедури :ref:`frameworks_has_items`

.. sourcecode::

    hasItems = true | false

Висока деталізація відбору визначає,
що всі питання/скраги до предмету закупівлі будуть вирішені на етпапі відбору.
закупівля буде, відповідно, - коротка.

Закупівля
---------

Другий етап у вигляді закупівлі посилається на угоду. 

Якщо угода має деталізацію предмету закупівлі ("hasItems": true),
то закупівля буде скороченою без оскарження.

:ref:`competitiveordering_short_tutorial`

Якщо ж угода не має деталізації предмету закупівлі ("hasItems": false),
то закупівля буде довгою.

:ref:`competitiveordering_long_tutorial`

Різниця між коротким і довгим тендером визначається уточненими конфіураціями. 
