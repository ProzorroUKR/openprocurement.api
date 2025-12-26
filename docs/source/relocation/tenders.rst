Приклад для закупівлі
---------------------

Зміна власника закупівлі
~~~~~~~~~~~~~~~~~~~~~~~~

Переглянемо приклад зміни власника для закупівлі.


Створення закупівлі
^^^^^^^^^^^^^^^^^^^

Спочатку створимо закупівлю:

.. http:example:: tutorial/create-tender.http
   :code:

Майданчик `broker` є поточним власником ``owner`` закупівлі.

Зверніть увагу, що секція відповіді `access` містить ключ ``transfer``, який використовується для зміни власника закупівлі. 

Після реєстрація закупівлі в ЦБД майданчик повинен довести ключ ``transfer`` до відома клієнта.

Ініціація зміни власника
^^^^^^^^^^^^^^^^^^^^^^^^

Майданчик, що стане новим власником закупівлі, повинен створити об'єкт `Transfer`.

.. http:example:: tutorial/create-tender-transfer.http
   :code:

Об'єкт `Transfer` містить новий ключ доступу ``token`` та новий ключ ``transfer`` для об'єкта, власник якого буде змінений.

Об'єкт `Transfer` можна переглянути за допомогою ідентифікатора `id`:

.. http:example:: tutorial/get-tender-transfer.http
   :code:

Зміна власника закупівлі
^^^^^^^^^^^^^^^^^^^^^^^^

Можливість зміни власника закупівлі залежить від статусу закупівлі:

+----------------------------------------+-----------------------+
| Дозволено                              | Не дозволено          |
+----------------------------------------+-----------------------+
| **belowThreshold**                     |                       |
+----------------------------------------+-----------------------+
| active.enquiries                       | complete              |
|                                        |                       |
| active.tendering                       | cancelled             |
|                                        |                       |
| active.auction                         | unsuccessful          |
|                                        |                       |
| active.qualification                   |                       |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **aboveThresholdUA**                   |                       |
+----------------------------------------+-----------------------+
| active.tendering                       | complete              |
|                                        |                       |
| active.auction                         | cancelled             |
|                                        |                       |
| active.qualification                   | unsuccessful          |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **aboveThresholdEU**                   |                       |
+----------------------------------------+-----------------------+
| active.tendering                       | complete              |
|                                        |                       |
| active.pre-qualification               | cancelled             |
|                                        |                       |
| active.pre-qualification.stand-still   | unsuccessful          |
|                                        |                       |
| active.auction                         |                       |
|                                        |                       |
| active.qualification                   |                       |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **aboveThresholdUA.defense**           |                       |
+----------------------------------------+-----------------------+
| active.tendering                       | complete              |
|                                        |                       |
| active.auction                         | cancelled             |
|                                        |                       |
| active.qualification                   | unsuccessful          |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **competitiveDialogueUA**              |                       |
+----------------------------------------+-----------------------+
| active.tendering                       | active.stage2.waiting |
|                                        |                       |
| active.pre-qualification               | complete              |
|                                        |                       |
| active.pre-qualification.stand-still   | unsuccessful          |
|                                        |                       |
| active.stage2.pending                  | cancelled             |
+----------------------------------------+-----------------------+
| **competitiveDialogueUA.stage2**       |                       |
+----------------------------------------+-----------------------+
| draft.stage2                           | complete              |
|                                        |                       |
| active.tendering                       | unsuccessful          |
|                                        |                       |
| active.auction                         | cancelled             |
|                                        |                       |
| active.qualification                   |                       |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **competitiveDialogueEU**              |                       |
+----------------------------------------+-----------------------+
| active.tendering                       | active.stage2.waiting |
|                                        |                       |
| active.pre-qualification               | complete              |
|                                        |                       |
| active.pre-qualification.stand-still   | unsuccessful          |
|                                        |                       |
| active.stage2.pending                  | cancelled             |
+----------------------------------------+-----------------------+
| **competitiveDialogueEU.stage2**       |                       |
+----------------------------------------+-----------------------+
| draft.stage2                           | complete              |
|                                        |                       |
| active.tendering                       | unsuccessful          |
|                                        |                       |
| active.pre-qualification               | cancelled             |
|                                        |                       |
| active.pre-qualification.stand-still   |                       |
|                                        |                       |
| active.auction                         |                       |
|                                        |                       |
| active.qualification                   |                       |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **esco**                               |                       |
+----------------------------------------+-----------------------+
| active.tendering                       | complete              |
|                                        |                       |
| active.pre-qualification               | unsuccessful          |
|                                        |                       |
| active.pre-qualification.stand-still   | cancelled             |
|                                        |                       |
| active.auction                         |                       |
|                                        |                       |
| active.qualification                   |                       |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **closeFrameworkAgreementUA**          |                       |
+----------------------------------------+-----------------------+
| active.tendering                       | complete              |
|                                        |                       |
| active.pre-qualification               | unsuccessful          |
|                                        |                       |
| active.pre-qualification.stand-still   | cancelled             |
|                                        |                       |
| active.auction                         |                       |
|                                        |                       |
| active.qualification                   |                       |
|                                        |                       |
| active.qualification.stand-still       |                       |
|                                        |                       |
| active.awarded                         |                       |
+----------------------------------------+-----------------------+
| **closeFrameworkAgreementSelectionUA** |                       |
+----------------------------------------+-----------------------+
| draftactive.enquiries                  | draft.pending         |
|                                        |                       |
| active.tendering                       | draft.unsuccessful    |
|                                        |                       |
| active.auction                         | complete              |
|                                        |                       |
| active.qualification                   | unsuccessful          |
|                                        |                       |
| active.awarded                         | cancelled             |
+----------------------------------------+-----------------------+
| **reporting**                          |                       |
+----------------------------------------+-----------------------+
| active                                 | complete              |
|                                        |                       |
|                                        | cancelled             |
+----------------------------------------+-----------------------+
| **negotiation**                        |                       |
+----------------------------------------+-----------------------+
| active                                 | complete              |
|                                        |                       |
|                                        | cancelled             |
+----------------------------------------+-----------------------+
| **negotiation.quick**                  |                       |
+----------------------------------------+-----------------------+
| active                                 | complete              |
+----------------------------------------+-----------------------+

Щоб змінити власника закупівлі новий майданчик повинен надіслати POST запит на відповідний  `/tenders/id/` з секцією `data`, що міститиме ідентифікатор ``id`` для `Transfer` та ключ ``transfer`` отриманий від клієнта:

.. http:example:: tutorial/change-tender-ownership.http
   :code:

Оновлене значення властивості ``owner`` вказує, що власник був успішно змінений. 

Зверніть увагу, що новий майданчик повинен довести до відома клієнта новий ключ ``transfer`` (згенерований в об'єкті `Transfer`).

Після того, як об'єкт `Transfer` було застосовано, для нього генерується властивість ``usedFor`` (вказується шлях до об'єкта, власника якого було змінено):

.. http:example:: tutorial/get-used-tender-transfer.http
   :code:

'Використаний' об'єкт `Transfer` вже не можна застосувати до іншого об'єкта.

Спробуємо змінити закупівлю за допомогою ключа ``token``, отриманого при створенні об'єкта `Transfer`.

.. http:example:: tutorial/modify-tender.http
   :code:

Зверніть увагу, що тільки майданчик з відповідним рівнем акредитації може стати новим власником. В іншому випадку майданчику така дія буде заборонена.

.. http:example:: tutorial/change-tender-ownership-forbidden.http
   :code:

Зміна власника дозволена тільки якщо поточний власник тендера має спеціальний рівень акредетації, що дозволяє зміну:

.. http:example:: tutorial/change-tender-ownership-forbidden-owner.http
   :code:
