.. _law4888_criteria:

Критерії за Законом № 4888
==========================

Базові операції над критеріями, групами вимог, вимогами та прийнятними доказами не змінюються - вони
описані в розділі :ref:`criteria_operation`. Нижче наведені лише відмінності, які діють у процедурах за
Законом № 4888.

Критерії відбору (стаття 20)
----------------------------

Замість критеріїв статті 16 у процедурах за Законом № 4888 використовуються критерії відбору статті 20.
`Стандарт можна отримати тут
<https://github.com/ProzorroUKR/standards/blob/master/criteria/law_4888/tender/selection_criteria.json>`__

.. list-table::
   :header-rows: 1

   * - ``classification.id``
     - Назва
     - Підстава
   * - ``CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.TECHNICAL.EQUIPMENT``
     - Наявність обладнання, матеріально-технічної бази та технологій
     - Пункт 1 частини 2 статті 20
   * - ``CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.TECHNICAL.STAFF_FOR_CARRYING_SCOPE``
     - Наявність працівників відповідної кваліфікації
     - Пункт 2 частини 2 статті 20
   * - ``CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.REFERENCES.WORKS_PERFORMANCE``
     - Наявність досвіду виконання аналогічного договору (договорів)
     - Пункт 3 частини 2 статті 20
   * - ``CRITERION.SELECTION.ECONOMIC_FINANCIAL_STANDING``
     - Наявність фінансової спроможності
     - Пункт 4 частини 2 статті 20

Особливості цих критеріїв:

- ``classification.scheme`` - ``LAW4888``, ``source`` - ``tenderer``, ``relatesTo`` - ``lot``;
- у ``legislation`` разом з полем ``article`` передається його англомовний відповідник ``article_en``;
- якщо ``mainProcurementCategory`` закупівлі - ``works`` або ``services``, закупівлю не можна оголосити
  (перевести зі статусу ``draft``) без щонайменше одного критерію відбору; для ``goods`` критерії відбору
  не обов'язкові, але можуть бути додані;
- перелік обов'язкових критеріїв для кожної процедури визначається довідником
  ``criteria/rules/<procurementMethodType>.json`` у `standards
  <https://github.com/ProzorroUKR/standards/tree/master/criteria/rules>`_.

Перевірка обов'язкових критеріїв по лотах
-----------------------------------------

Якщо закупівля має лоти, набір обов'язкових критеріїв перевіряється для кожного активного лоту окремо, а не
для закупівлі в цілому:

- критерій зараховується лоту, якщо ``relatesTo`` = ``lot`` і ``relatedItem`` містить ``id`` цього лоту;
- критерій з ``relatesTo`` = ``tender`` зараховується всім лотам;
- критерій, усі вимоги якого переведені у статус ``cancelled``, не враховується;
- лоти у статусі ``cancelled`` не перевіряються.

Додамо критерій відбору лише до першого лоту і спробуємо оголосити закупівлю - система повідомить, якого
критерію бракує другому лоту:

.. http:example:: http/activate-tender-without-selection-criteria.http
   :code:

Додамо критерій відбору до другого лоту:

.. http:example:: http/add-selection-criteria-second-lot.http
   :code:

Тепер закупівлю можна оголосити:

.. http:example:: http/activate-tender.http
   :code:

Прийнятні докази критеріїв
--------------------------

Для прийнятних доказів (``eligibleEvidences``) діють додаткові правила:

- ``title`` обов'язковий і не може бути порожнім;
- доказ з ``type`` = ``document`` обов'язково містить ``relatedDocument``;
- ``relatedDocument`` має посилатися на документ закупівлі з ``documentType`` = ``evaluationCriteria``.

Правила перевіряються в усіх запитах, які створюють або змінюють докази: POST та PATCH критеріїв, груп
вимог, вимог і доказів, а також PUT вимоги у статусах ``active.enquiries`` та ``active.tendering``.

Доказ без назви:

.. http:example:: http/criteria-evidence-title-required.http
   :code:

Доказ типу ``document`` без ``relatedDocument``:

.. http:example:: http/criteria-evidence-document-required.http
   :code:

Доказ, що посилається на документ з іншим ``documentType``:

.. http:example:: http/criteria-evidence-invalid-document-type.http
   :code:

Завантажимо документ з ``documentType`` = ``evaluationCriteria``:

.. http:example:: http/add-evaluation-criteria-document.http
   :code:

Тепер критерій можна створити:

.. http:example:: http/add-selection-criteria.http
   :code:

Докази у відповідях на вимоги
-----------------------------

Докази, які подаються разом з відповідями на вимоги (``requirementResponses`` пропозиції, рішення про
визначення переможця та попередньої кваліфікації), теж мають посилатися на документ певного типу:

- документ має бути завантажений у ``documents`` відповідного об'єкта; документи з ``eligibilityDocuments``,
  ``financialDocuments`` та ``qualificationDocuments`` для доказів не приймаються;
- документ має мати ``documentType`` = ``qualificationDocuments``;
- якщо документ має кілька версій, перевіряється ``documentType`` останньої версії.

Спроба подати доказ з документом пропозиції (``documentType`` = ``proposal``):

.. http:example:: http/bid-evidence-invalid-document-type.http
   :code:

Завантажимо документ з ``documentType`` = ``qualificationDocuments``:

.. http:example:: http/add-bid-qualification-document.http
   :code:

Тепер пропозицію з доказом можна активувати:

.. http:example:: http/activate-bid-with-evidence.http
   :code:
