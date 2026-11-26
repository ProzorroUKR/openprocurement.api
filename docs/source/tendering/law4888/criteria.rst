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

Критерії відмови в участі (стаття 21)
-------------------------------------

Замість критеріїв статті 17 у процедурах за Законом № 4888 використовуються підстави для відмови в участі
у процедурі закупівлі, визначені статтею 21. `Стандарт можна отримати тут
<https://github.com/ProzorroUKR/standards/blob/master/criteria/law_4888/tender/exclusion_criteria.json>`__

.. list-table::
   :header-rows: 1

   * - ``classification.id``
     - Назва
     - ``source``
     - Підстава
   * - ``CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION``
     - Наявність впливу на прийняття рішення замовника
     - ``procuringEntity``
     - Пункт 1 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION``
     - Вчинення корупційних правопорушень
     - ``winner``
     - Пункт 2 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONVICTIONS.FRAUD``
     - Вчинення економічних правопорушень
     - ``tenderer``
     - Пункт 4 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION``
     - Вчинення кримінальних правопорушень
     - ``tenderer``
     - Пункт 5 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION``
     - Наявність зв'язку суб'єкта господарювання з іншими учасниками процедури або замовником
     - ``procuringEntity``
     - Пункт 7 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY``
     - Порушення справи про банкрутство
     - ``tenderer``
     - Пункт 8 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.NATIONAL.OTHER``
     - Наявність інших підстав для відмови в участі у процедурі закупівлі
     - ``tenderer``
     - Пункт 9 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.NATIONAL.ANTI-CORRUPTION``
     - Наявність антикорупційної програми
     - ``tenderer``
     - Пункт 10 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONVICTIONS.TERRORIST_OFFENCES``
     - Вчинення правопорушень, пов'язаних із застосуванням санкцій
     - ``tenderer``
     - Пункт 11 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING``
     - Вчинення правопорушень, пов'язаних з використанням дитячої праці чи торгівлею людьми
     - ``winner``
     - Пункт 12 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES``
     - Наявність заборгованості зі сплати податків і зборів
     - ``winner``
     - Пункт 13 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.PROCEDURE_PREPARATION``
     - Отримання конкурентної переваги або порушення принципу недискримінації
     - ``tenderer``
     - Пункт 14 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.PROCEDURE_PARTICIPATION``
     - Конфлікт інтересів без можливості врегулювання
     - ``tenderer``
     - Пункт 15 частини 1 статті 21
   * - ``CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.EARLY_TERMINATION``
     - Наявність не виконаних зобов'язань за раніше укладеним договором
     - ``winner``
     - Частина 2 статті 21
   * - ``CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.MANAGEMENT.SUBCONTRACTING_PROPORTION``
     - Інформування про субпідрядників/співвиконавців
     - ``winner``
     - Частина 6 статті 21

Особливості цих критеріїв:

- ``classification.scheme`` - ``LAW4888``, ``relatesTo`` - ``tender``; виняток -
  ``CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.MANAGEMENT.SUBCONTRACTING_PROPORTION``, який має
  ``relatesTo`` - ``lot`` і тому додається для кожного лоту окремо;
- ``source`` визначає, хто відповідає на вимоги критерію: ``tenderer`` - учасник у складі пропозиції,
  ``winner`` - учасник, якого визначено переможцем, ``procuringEntity`` - замовник у рішенні про визначення
  переможця або в попередній кваліфікації;
- в ``openTendering`` обов'язковими є всі критерії статті 21, крім
  ``CRITERION.EXCLUSION.NATIONAL.ANTI-CORRUPTION``; критерій субпідряду обов'язковий лише для
  ``mainProcurementCategory`` = ``works`` або ``services``;
- перелік обов'язкових критеріїв для кожної процедури визначається довідником
  ``criteria/rules/<procurementMethodType>.json`` у `standards
  <https://github.com/ProzorroUKR/standards/tree/master/criteria/rules>`_.

Інші обов'язкові критерії
-------------------------

Крім критеріїв статей 20 і 21, обов'язковими можуть бути й інші критерії з довідника
``criteria/law_4888/tender/other_criteria.json`` - їх перелік залежить від процедури і визначається
довідником ``criteria/rules/<procurementMethodType>.json`` у `standards
<https://github.com/ProzorroUKR/standards/tree/master/criteria/rules>`_. Наприклад, для ``openTendering``
такими є ``CRITERION.OTHER.BID.LANGUAGE`` - мова тендерної пропозиції та
``CRITERION.OTHER.BID.VALIDITY_PERIOD`` - строк її дії; обидва мають ``relatesTo`` - ``tender``, тому
додаються один раз на закупівлю:

.. http:example:: http/add-other-criteria.http
   :code:

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

Поля критерію з довідника
-------------------------

Для частини критеріїв окремі поля мають збігатися з довідником ``criteria/law_4888`` у `standards
<https://github.com/ProzorroUKR/standards/tree/master/criteria/law_4888>`_ і замовник не може задати їм
власне значення. Зараз так перевіряється ``relatesTo`` критерію ``CRITERION.OTHER.BID.GUARANTEE``:
забезпечення тендерної пропозиції встановлюється лоту, тому критерій створюється з ``relatesTo`` = ``lot``
та ``relatedItem`` = ``id`` лоту.

Перевірка виконується у кожному запиті, який створює або змінює критерій, і стосується лише тих критеріїв,
які передані в запиті:

.. http:example:: http/criteria-bid-guarantee-relates-to.http
   :code:

Прийнятні докази критеріїв
--------------------------

Для прийнятних доказів (``eligibleEvidences``) діють додаткові правила:

- ``title`` обов'язковий і не може бути порожнім;
- доказ з ``type`` = ``document`` обов'язково містить ``relatedDocument``;
- ``relatedDocument`` має посилатися на документ закупівлі, ``documentType`` якого залежить від критерію:

.. list-table::
   :header-rows: 1

   * - Критерій
     - ``documentType`` документа закупівлі
   * - критерії відбору статті 20
     - ``evaluationCriteria``
   * - критерії відмови в участі статті 21
     - ``eligibilityCriteria``
   * - ``CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.MANAGEMENT.SUBCONTRACTING_PROPORTION``
     - ``evaluationCriteria``

Правила перевіряються в усіх запитах, які створюють або змінюють докази: POST та PATCH критеріїв, груп
вимог, вимог і доказів, а також PUT вимоги у статусах ``active.enquiries`` та ``active.tendering``.

Оскільки в одному запиті може бути кілька вимог, у тексті помилки вказується ``id`` вимоги, доказ якої
не пройшов перевірку.

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

Для критеріїв статті 21 той самий документ не підходить - потрібен ``eligibilityCriteria``:

.. http:example:: http/exclusion-criteria-invalid-document-type.http
   :code:

Завантажимо документ з ``documentType`` = ``eligibilityCriteria``:

.. http:example:: http/add-eligibility-criteria-document.http
   :code:

Тепер критерії відмови в участі можна створити:

.. http:example:: http/add-exclusion-criteria.http
   :code:

Докази у відповідях на вимоги
-----------------------------

Докази, які подаються разом з відповідями на вимоги (``requirementResponses`` пропозиції, рішення про
визначення переможця та попередньої кваліфікації), теж мають посилатися на документ певного типу. Контейнер
документів і ``documentType`` залежать від критерію:

.. list-table::
   :header-rows: 1

   * - Критерій
     - Об'єкт і контейнер документа
     - ``documentType``
   * - критерії відбору статті 20
     - ``documents`` пропозиції
     - ``qualificationDocuments``
   * - критерії статті 21 з ``source`` ``tenderer`` / ``winner``
     - ``eligibilityDocuments`` пропозиції
     - ``eligibilityDocuments``
   * - ``...SUBCONTRACTING_PROPORTION``
     - ``qualificationDocuments`` пропозиції
     - ``qualificationDocuments``
   * - критерії статті 21 з ``source`` ``procuringEntity``
     - ``documents`` рішення про визначення переможця або попередньої кваліфікації
     - ``eligibilityDocuments``

Документ з іншого контейнера для доказу не приймається. Якщо документ має кілька версій, перевіряється
``documentType`` останньої версії. У тексті помилки вказується ``id`` вимоги, доказ якої не пройшов
перевірку.

Спроба подати доказ критерію відбору з документом пропозиції (``documentType`` = ``proposal``):

.. http:example:: http/bid-evidence-invalid-document-type.http
   :code:

Завантажимо документ з ``documentType`` = ``qualificationDocuments``:

.. http:example:: http/add-bid-qualification-document.http
   :code:

Для критерію статті 21 цей документ не підходить - він лежить у ``documents``, а не в
``eligibilityDocuments``:

.. http:example:: http/bid-exclusion-evidence-invalid-document-type.http
   :code:

Завантажимо документ у ``eligibilityDocuments``:

.. http:example:: http/add-bid-eligibility-document.http
   :code:

Тепер пропозицію з доказами можна активувати:

.. http:example:: http/activate-bid-with-evidence.http
   :code:

Підстави для відмови на етапі визначення переможця
--------------------------------------------------

Відповіді замовника на вимоги критеріїв з ``source`` = ``procuringEntity`` подаються в рішенні про
визначення переможця. Позитивна відповідь на два з них означає, що учасника має бути відхилено, тому
рішення не можна перевести у статус ``active``:

- ``CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION`` - наявність впливу на прийняття рішення
  замовника;
- ``CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION`` - наявність зв'язку суб'єкта господарювання з іншими
  учасниками процедури або замовником.

Перевірка діє лише в процедурах за Законом № 4888 і враховує лише відповіді зі значенням ``true``.

Додамо відповіді зі значенням ``true``:

.. http:example:: http/award-exclusion-responses.http
   :code:

Спроба визначити такого учасника переможцем:

.. http:example:: http/activate-award-with-exclusion-grounds.http
   :code:

Після того як замовник змінить відповіді на ``false``, рішення можна активувати:

.. http:example:: http/activate-award.http
   :code:

У закупівлях з попередньою кваліфікацією (``config.hasPrequalification`` = ``true``) ті самі перевірки
діють і для об'єкта ``qualification``: позитивна відповідь на ці критерії не дозволяє перевести
попередню кваліфікацію у статус ``active``.
