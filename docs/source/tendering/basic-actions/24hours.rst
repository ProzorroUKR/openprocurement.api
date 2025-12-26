.. _24hours:

"24 години"
===========

Під час кваліфікаційного процесу (або попередньої кваліфікації, якщо процедура має таку), замовник може прийняти рішення дозволити учаснику торгів дозавантажувати документи до своєї заявки, додавати/змінювати `evidences` у вигляді файлів або змінити ряд полів у своїй пропозиції.

Поля, які дозволено змінювати при застосуванні `milestone:code:24h`:

* requirementResponses
* items.unit.value.amount
* subcontractingDetails
* lotValues.subcontractingDetails
* tenderers.signerInfo


Приклад розміщення :ref:`qualificationmilestone` для кваліфікації

.. http:example:: ./http/24hours/award-milestone-post.http
   :code:


Приклад попередньої кваліфікації


.. http:example:: ./http/24hours/qualification-milestone-post.http
   :code:

Після додавання майлстоуну виправлення невідповідностей `24h`, award/qualification має бути підписаний через додавання файлу `documentType: deviationReport`.

Підписання :ref:`qualificationmilestone` для кваліфікації:

.. http:example:: ./http/24hours/award-sign-milestone-24.http
   :code:

Підписання попередньої кваліфікації:

.. http:example:: ./http/24hours/qualification-sign-milestone-24.http
   :code:

Тільки один документ з типом `deviationReport` може бути доданий до award/qualification:

.. http:example:: ./http/24hours/award-sign-milestone-24-duplicate.http
   :code:

Поле “dueDate” у відповіді вказує на кінець періоду, під час якого замовник не може прийняти рішення щодо об’єкта кваліфікації


.. http:example:: ./http/24hours/award-patch.http
   :code:


Учасник торгів може розмістити нові документи на свою заявку


.. http:example:: ./http/24hours/post-doc.http
   :code:


Учасник торгів може оновити свої документи

.. http:example:: ./http/24hours/put-doc.http
   :code:


Учасник торгів може змінити ряд полів у своїй пропозиції:

.. http:example:: ./http/24hours/patch-bid.http
   :code:

Якщо це поля, які змінювати заборонено, то ми побачимо помилку:

.. http:example:: ./http/24hours/patch-bid-invalid.http
   :code:

Учасник торгів може змінювати відповіді на критерії `requirementResponses` у своїй пропозиції.

Наприклад, учасник може видалити попередню відповідь на одну `requirementGroup` статті 17:

.. http:example:: ./http/24hours/delete-article-17-req-response.http
   :code:

і натомість надати відповідь на іншу `requirementGroup` статті 17:

.. http:example:: ./http/24hours/add-article-17-req-response.http
   :code:

Учасник може додавати/змінювати `evidences` у вигляді файлів:

.. http:example:: ./http/24hours/add-req-responses-evidences.http
   :code:

Після закінчення `milestone.dueDate` в учасника немає можливості змінювати поля пропозиції:

.. http:example:: ./http/24hours/patch-bid-forbidden.http
   :code:
