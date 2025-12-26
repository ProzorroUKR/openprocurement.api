
.. include:: defs.hrst

.. index:: Tender, Auction
.. _tender:

Tender
======

Схема
-----

:title:
   рядок, багатомовний

   Додатково у :ref:`openeu`, :ref:`esco` та :ref:`competitivedialogue` (stage2_EU):

       uk (title) та en (title_en) переклади обов’язкові

   Назва тендера, яка відображається у списках. Можна включити такі елементи:

   * код закупівлі (у системі управління організації-замовника)
   * періодичність закупівлі (щороку, щокварталу, і т.д.)
   * елемент, що закуповується
   * інша інформація

:description:
   рядок, багатомовний

   Детальний опис закупівлі.

:tenderID:
   рядок, генерується автоматично, лише для читання

   Ідентифікатор закупівлі, щоб знайти закупівлю у "паперовій" документації. 

   |ocdsDescription| Ідентифікатор тендера `TenderID` повинен завжди співпадати з OCID. Його включають, щоб зробити структуру даних більш зручною.

:procuringEntity:
   :ref:`ProcuringEntity`, обов’язково

   Замовник (організація, що проводить закупівлю).

   |ocdsDescription| Об’єкт, що управляє закупівлею. Він не обов’язково є покупцем, який платить / використовує закуплені елементи.

   Якщо :code:`procurementMethodType` має значення :code:`negotiation` або :code:`negotiation.quick`, тоді можливі значення :code:`ProcuringEntity.kind` обмежені :code:`[‘general’, ‘special’, ‘defense’]`.

:procurementMethod:
    рядок, генерується автоматично

    :`limited`:

    Метод закупівлі тендеру.

    Тільки у :ref:`limited`


:procurementMethodType:
    рядок

    :`belowThreshold`:
        ідентифікатор до порогової процедури

    :`aboveThresholdUA`:
        ідентифікатор вище порогової процедури

    :`aboveThresholdEU`:
        вище порогового ідентифікатора процедури з публікацією на англійській мові

    :`aboveThresholdUA.defense`:
        ідентифікатор процедури для потреб оборони

    :`reporting`:
        ідентифікатор процедури звітування

    :`negotiation`:
        ідентифікатор процедури переговорів

    :`negotiation.quick`:
        ідентифікатор процедури швидких переговорів

    :`esco`:
        ідентифікатор процедури esco

    :`closeFrameworkAgreementUA`:
        closeframeworkagreementua procedure indentifier

    :`closeFrameworkAgreementSelectionUA`:
        closeframeworkagreementua.selection procedure indentifier


    Можливі значення у :ref:`competitivedialogue` stage1:

    :`competitiveDialogueEU`:

    :`competitiveDialogueUA`:

    Можливі значення у :ref:`competitivedialogue` stage2:

    :`competitiveDialogueEU.stage2`:

    :`competitiveDialogueUA.stage2`:


:value:
   :ref:`value`, обов’язково

   Повний доступний бюджет закупівлі. Пропозиції, що більші за ``value`` будуть відхилені.

   |ocdsDescription| Загальна кошторисна вартість закупівлі.

   Відсутнє в :ref:`esco`

:guarantee:
    :ref:`BasicValue`

    Забезпечення тендерної пропозиції

:date:
    рядок, :ref:`date`, генерується автоматично
                                           
:items:
   список об’єктів :ref:`item`, обов’язково

   Список, який містить елемент, що закуповується. 

   |ocdsDescription| Товари та послуги, що будуть закуплені, поділені на спискові елементи, де це можливо. Елементи не повинні дублюватись, замість цього вкажіть кількість 2.

:features:
   список об’єктів :ref:`Feature`

   Властивості закупівлі.

:documents:
   Список об’єктів :ref:`document`
 
   |ocdsDescription| Всі документи та додатки пов’язані із закупівлею.

:questions:
   Список об’єктів :ref:`question`

   Звернення до замовника ``procuringEntity`` і відповіді на них.

:complaints:
   |   Список об’єктів :ref:`Complaint` та :ref:`Claim`.
   |   Список об’єктів :ref:`Claim` для `belowThreshold`.

   Скарги та Вимоги на умови закупівлі та їх вирішення.

:bids:
   Список об’єктів :ref:`bid`

   Список усіх пропозицій зроблених під час закупівлі разом із інформацією про учасників закупівлі, їхні пропозиції та інша кваліфікаційна документація.

   |ocdsDescription| Список усіх компаній, які подали заявки для участі у закупівлі.

:minimalStep:
   :ref:`value`, обов'язково для безлотових закупівель з аукціоном

   Мінімальний крок аукціону (редукціону). Правила валідації:

   * Значення `amount` повинно бути меншим за `Tender.value.amount` та в межах 0.5%-3% від `Tender.value.amount`
   * Значення `currency` повинно бути або відсутнім, або співпадати з `Tender.value.currency`
   * Значення `valueAddedTaxIncluded` повинно бути або відсутнім, або співпадати з `Tender.value.valueAddedTaxIncluded`

    Відсутнє в :ref:`esco`

:awards:
    Список об’єктів :ref:`award`

    Усі  кваліфікації (дискваліфікації та переможці).

:agreements:
    Список об’єктів :ref:`Agreement <agreement_cfaua>`

    Тільки у :ref:`cfaua` та :ref:`cfaselectionua`

:agreement:
    Об’єкт :ref:`Agreement <agreement_pricequotation>`

    Тільки у :ref:`pricequotation`

:contracts:
    Список об’єктів :ref:`Contract`

:enquiryPeriod:
   :ref:`period`, обов’язково

   Період, коли дозволено подавати звернення. Повинна бути вказана хоча б `endDate` дата.

   |ocdsDescription| Період, коли можна зробити уточнення та отримати відповіді на них.

   Додатково у :ref:`defense`, :ref:`openua` та :ref:`openeu`:
      `enquiryPeriod` має додаткові поля:

      * ``invalidationDate`` - це дата останньої зміни умов, коли всі подані цінові пропозиції перейшли в стан `invalid`. Відповідно необхідні дії майданчика щодо активації чи переподачі пропозицій.

      * ``clarificationsUntil``- час, до якого можна давати відповіді на зернення та вимоги, після якого блокується процедура.

:dateModified:
    рядок, :ref:`date`, генерується автоматично

:owner:
    рядок, генерується автоматично

:tenderPeriod:
   :ref:`period`, обов’язково

   Період, коли подаються пропозиції. Повинна бути вказана хоча б `endDate` дата.

   |ocdsDescription| Період, коли закупівля відкрита для подачі пропозицій. Кінцева дата - це дата, коли перестають прийматись пропозиції.

:qualificationPeriod:
   :ref:`period`,  лише для читання

   Цей період включає кваліфікацію та 10-денний період блокування.

   |ocdsDescription| Період, коли кваліфікацію можна подати з періодом блокування.

   Тільки у :ref:`openeu`, :ref:`esco` та :ref:`competitivedialogue`

:auctionPeriod:
   :ref:`period`,  лише для читання

   Період, коли проводиться аукціон.

:auctionUrl:
    url-адреса

    Веб-адреса для перегляду аукціону.

:awardPeriod:
   :ref:`period`,  лише для читання

   Період, коли відбувається визначення переможця.

   |ocdsDescription| Дата або період, коли очікується визначення переможця.

:mainProcurementCategory:
   рядок

   :`goods`:
       Основним предметом закупівлі являється продукція, об’єкти будь-якого виду та призначення, у тому числі сировина, вироби, устаткування, технології, предмети у твердому, рідкому і газоподібному стані, а також послуги, пов’язані з постачанням таких товарів, якщо вартість таких послуг не перевищує вартості самих товарів.

   :`services`:
       Основним предметом закупівлі являється проектування, будівництво нових, розширення, реконструкція, капітальний ремонт та реставрація існуючих об’єктів і споруд виробничого і невиробничого призначення, роботи з нормування в будівництві, геологорозвідувальні роботи, технічне переоснащення діючих підприємств та супровідні роботам послуги, у тому числі геодезичні роботи, буріння, сейсмічні дослідження, аеро- і супутникова фотозйомка та інші послуги, що включаються до кошторисної вартості робіт, якщо вартість таких послуг не перевищує вартості самих робіт.

   :`works`:
       Основним предметом закупівлі являється будь-який предмет закупівлі, крім товарів і робіт, зокрема транспортні послуги, освоєння технологій, наукові дослідження, науково-дослідні або дослідно-конструкторські розробки, медичне та побутове обслуговування, лізинг, найм (оренда), а також фінансові та консультаційні послуги, поточний ремонт.

   |ocdsDescription| Основна категорія, що описує основний об'єкт тендеру.

   Validation depends on:

        * :ref:`MPC_REQUIRED_FROM` constant

:milestones:

   Список об’єктів :ref:`Milestone`.


:plans:
   Список об’єктів :ref:`PlanRelation`.

:status:
   рядок

   :`active.enquiries`:
       Період уточнень (уточнення)
   :`active.tendering`:
       Очікування пропозицій (пропозиції)
   :`active.auction`:
       Період аукціону (аукціон)
   :`active.qualification`:
       Кваліфікація переможця (кваліфікація)
   :`active.awarded`:
       Пропозиції розглянуто (розглянуто)
   :`unsuccessful`:
       Закупівля не відбулась (не відбулась)
   :`complete`:
       Завершена закупівля (завершена)
   :`cancelled`:
       Відмінена закупівля (відмінена)

   Статус Закупівлі.

   Відмінності у :ref:`defense`, :ref:`openua` та :ref:`competitivedialogue` (UA):

   :`active.tendering`:
       Очікування пропозицій (пропозиції)
   :`active.auction`:
       Період аукціону (аукціон)
   :`active.qualification`:
       Кваліфікація переможця (кваліфікація)
   :`active.awarded`:
       Пропозиції розглянуто (розглянуто)
   :`unsuccessful`:
       Закупівля не відбулась (не відбулась)
   :`complete`:
       Завершена закупівля (завершена)
   :`cancelled`:
       Відмінена закупівля (відмінена)

   Відмінності у :ref:`limited`:

   :`active`:
       Активний тендер (за умовчанням)
   :`complete`:
       Завершений тендер
   :`cancelled`:
       Відмінена закупівля (відмінена)
   :`unsuccessful`:
       Закупівля не відбулась (не відбулась)

   Відмінності в :ref:`openeu`, :ref:`esco` та :ref:`competitivedialogue` (EU):

   :`active.tendering`:
       Період подання пропозицій та уточнень
   :`active.pre-qualification`:
       Перед-кваліфікаційний період
   :`active.pre-qualification.stand-still`:
       Блокування перед аукціоном
   :`active.auction`:
       Період аукціону (аукціон)
   :`active.qualification`:
       Кваліфікація переможця (кваліфікація)
   :`active.awarded`:
       Пропозиції розглянуто (розглянуто)
   :`complete`:
       Завершена закупівля (завершена)
   :`unsuccessful`:
       Закупівля не відбулась (не відбулась)
   :`cancelled`:
       Відмінена закупівля (відмінена)

   Відмінності у :ref:`cfaua`:

   :`active.tendering`:
       Очікування пропозицій (пропозиції)
   :`active.pre-qualification`:
       Пре-кваліфікаційній період (пре-кваліфікація)
   :`active.pre-qualification.stand-still`:
       Блокування перед аукціоном
   :`active.auction`:
       Період аукціону (аукціон)
   :`active.qualification`:
       Кваліфікація переможця (кваліфікація)
   :`active.qualification.stand-still`:
       Standstill before contract signing
   :`active.awarded`:
       Пропозиції розглянуто (розглянуто)
   :`unsuccessful`:
       Закупівля не відбулась (не відбулась)
   :`complete`:
       Завершена закупівля (завершена)
   :`cancelled`:
       Відмінена закупівля (відмінена)

   Відмінності :ref:`cfaselectionua`:

   :`draft`:
       ProcuringEntity creats draft of procedure, where should be specified procurementMethodType - closeFrameworkAgreementSelectionUA, procurementMethod - selective. One lot structure procedure. Also ProcuringEntity should specify agreement:id, items, title, description and features, if needed.
   :`draft.pending`:
       ProcuringEntity changes status of procedure from 'draft' to 'draft.pending' to make the system check provided information and pull up necassery information from :ref:`Agreement`.
   :`draft.unsuccessful`:
       Terminal status. System moves procedure to 'draft.unsuccessful' status if at least one of the checks is failed.
   :`active.enquiries`:
       Період уточнень (уточнення)
   :`active.tendering`:
       Очікування пропозицій (пропозиції)
   :`active.auction`:
       Період аукціону (аукціон)
   :`active.qualification`:
       Кваліфікація переможця (кваліфікація)
   :`active.awarded`:
       Пропозиції розглянуто (розглянуто)
   :`unsuccessful`:
       Закупівля не відбулась (не відбулась)
   :`complete`:
       Завершена закупівля (завершена)
   :`cancelled`:
       Відмінена закупівля (відмінена)

:lots:
   Список об’єктів :ref:`lot`.

   Містить всі лоти закупівлі.

   У :ref:`limited`: Тільки якщо `tender.procurementMethodType` є` negotiation` або `negotiation.quick`.

:agreementDuration:
   рядок, обов’язковий

   Duration of agreement. Maximum 4 years. Format ISO8601 (PnYnMnDTnHnMnS)

   Тільки у :ref:`cfaua`

:maxAwardsCount:
   рядок, обов’язковий

   Maximum number of required Awards

   Тільки у :ref:`cfaua`

:qualifications:

   Список об’єктів :ref:`Qualification`.

   Містить усі тендерні кваліфікації.

   Тільки у :ref:`openeu` та :ref:`competitivedialogue`

:cancellations:
   Список об’єктів :ref:`cancellation`.

   Містить 1 об’єкт зі статусом `active` на випадок, якщо закупівлю буде відмінено.

   Об’єкт :ref:`cancellation` описує причину скасування закупівлі та надає відповідні документи, якщо такі є.

:funders:
  Список об’єктів :ref:`organization`.

  Необов’язкове поле.

  Фінансування - суб’єкт, який надає грошові кошти або фінансує процес укладення договору.

:buyers:
   Перелік об'єктів :ref:`Buyer`, необхідний принаймні 1 об'єкт у випадку центральних закупівель

   Cуб’єкт(и) в інтересах якого(их) проводиться закупівля

:revisions:
   Список об’єктів :ref:`revision`, генерується автоматично, лише для читання

   Зміни властивостей об’єктів Закупівлі.


:cause:
    **Deprecated (нове поле CauseDetails)**

    рядок, обов’язковий для **переговорної** процедури та **переговорної процедури за нагальною потребою**. Також обов’язковий для **звітів**, які мають пусте поле `procurementMethodRationale`, в полі `procuringEntity.kind` вказано щось відмінне від `other` та очікувана вартість перевищує поріг:

        * 100 000 для товарів,
        * 200 000 для послуг,
        * 1 500 000 для робіт.

    Підстава для використання звітів, “звичайної” переговорної процедури або переговорної процедури за нагальною потребою. Для більш детальної інформації дивіться статтю 35 Закону України \”Про публічні закупівлі\”.

    Можливі значення зберігаються у довіднику `підстави <https://prozorroukr.github.io/standards/codelists/tender/tender_cause.json>`_.


    Тільки у :ref:`limited`

:causeDescription:
    **Deprecated (нове поле CauseDetails)**

    рядок, багатомовний

    Обгрунтування використання звітів, \”звичайної\” переговорної процедури або переговорної процедури за нагальною потребою.

    Тільки у :ref:`limited`

:causeDetails:
    :ref:`CauseDetails`, обов’язково

    Підстави та обгрунтування використання звітів.

    Тільки у :ref:`limited`

:stage2TenderID:
   рядок, генерується автоматично, лише для читання

   The tender identifier on second stage

   Тільки у :ref:`competitivedialogue` stage1

:shortlistedFirms:

    Список об’єктів :ref:`Firm`, генерується автоматично, лише для читання

    |ocdsDescription| Список усіх компаній, які подали заявки для участі у закупівлі

    Тільки у :ref:`competitivedialogue` stage2

:targets:
    Список об’єктів :ref:`Feature`

    Тільки для :ref:`cfaua`

    Може бути створений лише у якщо ``status`` тендера ``draft``. Модифікація можлива, тільки за умови, що ``status`` тендера один з [``draft``, ``active.tendering``]. В усіх інших випадках створення та модифікація заборонена.

Додатково у :ref:`esco`:

:NBUdiscountRate:
    float, обов’язково

    NBU Discount Rate as of tender notice publication date. Possible values: from 0 to 0.99 (from 0% to 99% respectively), with 3-digit precision after comma (e.g. 00.000). NBUdiscountRate change is interpreted as a change of tender conditions.


:minimalStepPercentage:
   :ref:`value`, Float, обов'язково для безлотових закупівель з аукціоном.

   Minimum step increment of the energy service contract performance indicator during auction that is calculated from  participant’s bid. Possible values: from 0.005 to 0.03 (from 0.5% to 3%), with 3-digit precision after comma.

:fundingKind:
    рядок, обов’язковий.

    Tender funding source. Possible values:
        * budget -  Budget funding.
        * other - exclusively supplier’s funding.

    Default value: other

:yearlyPaymentsPercentageRange:
    float, обов'язково для безлотових закупівель з аукціоном

    Fixed percentage of participant's cost reduction sum, with 3-digit precision after comma. Possible values:

        * from 0.8 to 1 (from 80% to 100% respectively) if tender:fundingKind:other.
        * from 0 to x, where x can vary from 0 to 0.8 (from 0% to x% respectively) if tender:fundingKind:budget.

:noticePublicationDate:
    рядок, :ref:`date`

    Генерується автоматично, лише для читання.

    Date of tender announcement.

:contractChangeRationaleTypes:
    object

    Генерується автоматично, лише для читання.

    Довідник з можливими причинами внесення змін до договору.

    Можливі значення:

        * `rationaleTypes для LAW 922 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_law_922.json>`_
        * `rationaleTypes для DECREE 1178 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_decree_1178.json>`_


.. important::

    Дати закупівлі повинні бути послідовними:

        * Поточний час
        * `enquiryPeriod.startDate`
        * `enquiryPeriod.endDate`
        * `tenderPeriod.startDate`
        * `tenderPeriod.endDate`


Робочий процес у :ref:`limited`
-------------------------------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="complete"]
        C [ label="cancelled"]
         A -> B;
         A -> C;
    }

\* позначає початковий стан
