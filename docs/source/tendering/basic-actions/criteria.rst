
.. _criteria_operation:

Базові операції над критеріями
------------------------------

Схема даних :ref:`критеріїв<criterion>`

Критерії - це частина тендерної документації, тому всі дії над критеріями може виконувати лише власник тендеру.

Створення критеріїв закупівлі
"""""""""""""""""""""""""""""

Критерії існують в наступних процедурах:  belowThreshold, aboveThreshold, aboveThresholdUA, aboveThresholdEU, competitiveOrdering, competitiveDialogueUA, competitiveDialogueEU, competitiveDialogueUA.stage2, competitiveDialogueEU.stage2, esco, closeFrameworkAgreementUA, closeFrameworkAgreementSelectionUA.

Критерії можуть бути пов'язані з tenderer, lot, item та tender. Ви не можете відмінити item, якщо існує хоча б один пов'язаний критерій з вимогою в статусі `active`. Щоб вказати кількість item рівною 0, необхідно перевести у статус `cancelled` всі активні вимоги пов'язаного критерію або видалити критерій (дозволено тільки для закупівель в статусі чернетка).

Можна створити одразу декілька критеріїв за один запит з повним набором даних.


.. http:example:: http/criteria/bulk-create-criteria.http
   :code:


Оновлення критерію закупівлі
""""""""""""""""""""""""""""

.. http:example:: http/criteria/patch-criteria.http
   :code:


Отримання інформації по критерію закупівлі
""""""""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/criteria-list.http
   :code:

.. http:example:: http/criteria/criteria.http
   :code:


Видалення критеріїв закупівлі
"""""""""""""""""""""""""""""

Поки закупівля в статусі чернетка дозволено видаляти критерій по `id`, використовуючи DELETE ендпоінт:

.. http:example:: http/criteria/delete-criteria.http
   :code:

Спробуємо видалити критерій, коли закупівля не в статусі `draft`, і отримаємо помилку:

.. http:example:: http/criteria/delete-criteria-invalid.http
   :code:


Базові операції над групами вимог
---------------------------------

Схема даних :ref:`групи вимог<RequirementGroup>`

Група вимог - це об'єкт який містить вимоги та встановлює правила: як та на які вимоги надавати відповідь.

В рамках групи вимог потрібно надати відповідь на всі вимоги(це означає відповісти на групу вимог). Якщо критеріон має більше однієї групи вимог, потрібно надати відповідь лише на одну групу. Якщо відповідь буде надана більше ніж на одну групу система поверне помилку.

:ref:`Тут ви можете побачити як це працює. <bid_activation_with_requirement_responses>`

Створення групи вимог
"""""""""""""""""""""

.. http:example:: http/criteria/add-criteria-requirement-group.http
   :code:


Оновлення групи вимог
"""""""""""""""""""""

.. http:example:: http/criteria/patch-criteria-requirement-group.http
   :code:

Отримання інформації по групам вимог
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/criteria-requirement-group-list.http
   :code:

.. http:example:: http/criteria/criteria-requirement-group.http
   :code:


Базові операції над вимогами
----------------------------

Схема даних :ref:`вимог<requirement>`

Створення вимоги
""""""""""""""""

.. http:example:: http/criteria/add-criteria-requirement.http
   :code:


Оновлення вимоги
""""""""""""""""
Ви можете використати PATCH метод для оновлення вимоги для тендеру в статусі чернетки.

.. http:example:: http/criteria/patch-criteria-requirement.http
   :code:

Для оновлення вимоги у `active.enquiries` та `active.tendering` статусах тендера необхідно використовувати метод PUT. Нова версія вимоги зі статусом `active` буде створена. Статус старої версії вимоги автоматично зміниться на `cancelled`.

.. http:example:: http/criteria/put-exclusion-criteria-requirement.http
   :code:

.. http:example:: http/criteria/criteria-requirement-list.http
   :code:

Видалення вимоги
""""""""""""""""
Щоби видалити вимогу з групи вимог, необхідно змінити статус вимоги на `cancelled`

.. http:example:: http/criteria/criteria-requirement-cancellation.http
   :code:

Отримання інформації по вимогам
"""""""""""""""""""""""""""""""

.. http:example:: http/criteria/criteria-requirement-list.http
   :code:

.. http:example:: http/criteria/criteria-requirement.http
   :code:

Базові операції над прийнятними доказами
----------------------------------------

Схема даних :ref:`прийнятних доказів<EligibleEvidence>`

Створення прийнятного доказу
""""""""""""""""""""""""""""
Щоби додати прийнятний доказ до тендеру у статусі чернетки, можна скористатись методом POST.

.. http:example:: http/criteria/add-requirement-evidence.http
   :code:

Щоби додати прийнятний доказ(и) до тендеру у статусі `active.enquiries` або `active.tendering`, необхідно використати метод PUT на рівні вимоги з вказанням розширеного списку eligibleEvidences. Нову версію вимоги зі статусом `active` та розширеним списком eligibleEvidences буде створено.

.. http:example:: http/criteria/requirement-put-add-evidence.http
   :code:

Оновлення інформації прийнятного доказу
"""""""""""""""""""""""""""""""""""""""
Щоби оновити прийнятний доказ до тендеру у статусі чернетки, можна скористатись методом PATCH.

.. http:example:: http/criteria/patch-requirement-evidence.http
   :code:

Щоб оновити прийнятний доказ(и) до тендеру у статусі `active.enquiries` або `active.tendering`, необхідно використати метод PUT на рівні вимоги з вказанням змінених вимог у списку eligibleEvidences. Нову версію вимоги зі статусом `active` та оновленими вимогами у списку eligibleEvidences буде створено.

.. http:example:: http/criteria/requirement-put-update-evidence.http
   :code:

Видалення прийнятного доказу
""""""""""""""""""""""""""""
Ви можете використати DELETE метод, щоб видалити доказ для тендера у статусі чернетки.

.. http:example:: http/criteria/delete-requirement-evidence.http
   :code:

Для видалення доказу в тендері у статусі `active.enquiries` або `active.tendering` необхідно використати метод PUT на рівні вимоги. Використовуйте список eligibleEvidences без деяких доказів, щоб видалити їх з вимоги. Щоб видалити всі прийнятні докази з вимоги використовуйте пустий список для поля eligibleEvidences.

.. http:example:: http/criteria/requirement-put-delete-evidence.http
   :code:

Для тендерів у статусі чернетки існує інша можливість для створення, оновлення та видалення доказів через PATCH запит на вимогу, де потрібно передати новий список `eligibleEvidences`:

.. http:example:: http/criteria/bulk-update-requirement-evidence.http
   :code:

.. http:example:: http/criteria/bulk-delete-requirement-evidence.http
   :code:

Отримання інформації по прийнятних доказах
""""""""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/requirement-evidences-list.http
   :code:

.. http:example:: http/criteria/requirement-evidence.http
   :code:


Виключні критерії
-----------------

Виключні критерії обов'язкові в наступних процедурах: `aboveThreshold`, `aboveThresholdUA`, `aboveThresholdEU`, `competitiveOrdering`, `competitiveDialogueUA`, `competitiveDialogueEU`, `esco`, `closeFrameworkAgreementUA`, `simple.defense`.

`Стандарт можна отримати тут <https://github.com/ProzorroUKR/standards/blob/master/criteria/article_17.json>`__

Неможливо перевести тендер у статус `active.tendering` без 11-ти вийняткових критеріїв та обов'язкових OTHER критеріїв:

.. http:example:: http/criteria/update-tender-status-without-exclusion-criteria-general.http
   :code:

Для закупівель `aboveThreshold`, `aboveThresholdEU` неможливо перевести тендер у статус `active.tendering` без 10-ти вийняткових та обов'язкових OTHER критеріїв:

.. http:example:: http/criteria/update-tender-status-without-exclusion-criteria-open.http
   :code:

Вийняткові критерії та всі дочірні об'єкти є незмінними:

.. http:example:: http/criteria/patch-exclusion-criteria.http
   :code:

.. http:example:: http/criteria/add-exclusion-criteria-requirement-group.http
   :code:

.. http:example:: http/criteria/patch-exclusion-criteria-requirement-group.http
   :code:

Для тендерів в статусі чернетки є можливість додавати вимоги вийняткових критеріїв:

.. http:example:: http/criteria/add-exclusion-criteria-requirement.http
   :code:

Для тендерів в статусі чернетки є можливість використати PATCH метод для оновлення вимоги вийняткових критеріїв:

.. http:example:: http/criteria/patch-exclusion-criteria-requirement.http
   :code:

Для статусів `active.enquiries` та `active.tendering` вимоги вийняткових критеріїв можливо редагувати методом PUT, але змінювати можна лише поля `status` та `eligibleEvidences`

.. http:example:: http/criteria/put-exclusion-criteria-requirement.http
   :code:

Схема роботи мовних критеріїв
"""""""""""""""""""""""""""""

Мовний критерій створюється так само як і інші та може бути включений до запиту на створення з іншими критеріями. Мова має бути вказана в `title`

.. http:example:: http-handwritten/criteria/create-language-criterion.http
   :code:

Але поле `eligibleEvidences` заборонено для цього критерію

.. http:example:: http-handwritten/criteria/update-language-criterion-with-evidence.http
   :code:

`expectedValue` може бути лише true

.. http:example:: http-handwritten/criteria/update-language-criterion-with-not-listed-lang.http
   :code:

Схема роботи критеріїв гарантії
-------------------------------

Гарантійне забезпечення пропозиції доступно для процедур: `belowThreshold`, `competitiveOrdering`, `aboveThreshold`, `aboveThresholdUA`, `aboveThresholdEU`, `esco`, `competitiveDialogueUA.stage2`, `competitiveDialogueEU.stage2`, `closeFrameworkAgreementUA`, `closeFrameworkAgreementSelectionUA`, `requestForProposal`, `simple.defense`.

Якщо вказаний даний критерій, тоді обов'язково мають бути вказані `guarantee` на рівні тендера, якщо критерій стосується тендера або `guarantee` на рівні лоту до якого застосовано критерій

.. http:example:: http-handwritten/criteria/create-bid-guarantee-criterion.http
   :code:

Гаратнійне забезпечення виконання умов договору доступно для процедур: `belowThreshold`, `competitiveOrdering`, `aboveThreshold`, `aboveThresholdUA`, `aboveThresholdEU`, `esco`, `competitiveDialogueUA`, `competitiveDialogueEU`, `competitiveDialogueUA.stage2`, `competitiveDialogueEU.stage2, `priceQuotation`, `closeFrameworkAgreementSelectionUA`, `requestForProposal`, `simple.defense`.

Для даного критерія `source` може бути лише `winner`. Докази `eligibleEvidences` можуть бути додані згідно :ref:`bidding`

.. http:example:: http-handwritten/criteria/create-contract-guarantee-criterion.http
   :code:

.. _criteria_workflow:

Схема роботи вийняткових критеріїв
""""""""""""""""""""""""""""""""""

.. graphviz::

      digraph G {
        rankdir = LR


        tender_draft [
            label = "draft*"
            shape = circle
            fixedsize = true
            width = .9
        ]

        tender_active_tendering [
            label = "active.\ntendering"
            shape = circle
            fixedsize = true
            width = .9
        ]

        bid_draft [
            label = "draft"
            shape = circle
            fixedsize = true
            width = .9
        ]

        bid_active [
            label = "active"
            shape = circle
            fixedsize = true
            width = .9
        ]

        tender_draft -> tender_active_tendering;
        bid_draft -> bid_active;
        bid_active -> create_bid_object;

        create_requirement_response_object [
            label = "Create requirement \nresponses"
            shape = rect
            style = filled
            fillcolor = plum
            fixedsize = true
            height = .5
            width = 2
        ]
        create_bid_object [
            label = "Create bid"
            shape = rect
            style = filled
            fillcolor = moccasin
            fixedsize = true
            height = .25
            width = 2
        ]
        create_criteria_object [
            label = "Create Criteria\n(11 Виключні критерії \nare required for \nsome procedures)"
            shape = rect
            style = filled
            fillcolor = lightsalmon
            fixedsize = true
            height = 1
            width = 2
        ]
        add_eligible_evidences_object [
            label = "Can be added \neligible evidences"
            shape = rect
            style = filled
            fillcolor = moccasin
            fixedsize = true
            height = .5
            width = 2
        ]

        block_patch_requirement_response_object [
            label = "Can't add or \nupdate requirement \nresponses and evidence"
            shape = rect
            style = filled
            fillcolor = moccasin
            fixedsize = true
            height = .75
            width = 2
        ]

        subgraph cluster_tender {
            label = "Tender"

            subgraph cluster_draft {
                label = ""
                style = filled
                color = plum
                tender_draft
                create_criteria_object
            }
            subgraph cluster_active {
                label = ""
                style = filled
                color = pink
                tender_active_tendering
                create_bid_object
                add_eligible_evidences_object
            }
        }
        subgraph cluster_bid {
            label = "Bid"

            subgraph cluster_draft {
                label = ""
                style = filled
                color = moccasin
                bid_draft
                create_requirement_response_object
            }
            subgraph cluster_active {
                label = ""
                style = filled
                color = mediumaquamarine
                bid_active
                block_patch_requirement_response_object
            }
        }
    }

Критерії статті 16
------------------

Критерії статті обов'язкові в наступних процедурах: `aboveThreshold`, `aboveThresholdUA`, `aboveThresholdEU`, `competitiveDialogueUA`, `competitiveDialogueEU`, `esco`, `closeFrameworkAgreementUA`.

`Стандарт можна отримати тут <https://github.com/ProzorroUKR/standards/blob/master/criteria/article_16.json>`__

Неможливо перевести тендер у статус `active.tendering` без хоча би одного критерію статті 16:

.. http:example:: http/criteria/update-tender-status-without-article-16-criteria.http
   :code:


Критерії оцінки вартості життєвого циклу
----------------------------------------

Критерій `Оцінка вартості життєвого циклу` доступний для процедур, в яких встановлено поле `awardCriteria` зі значенням `lifeCycleCost`.

Створимо процедуру з іншим значенням в полі `awardCriteria`:

.. http:example:: http/criteria/post-tender-award-criteria-lowest-cost.http
   :code:

Спробуємо додати критерій LCC і побачимо помилку:

.. http:example:: http/criteria/lcc-with-invalid-award-criteria.http
   :code:

Створимо процедуру зі значенням в полі `awardCriteria` встановленим `lifeCycleCost`:

.. http:example:: http/criteria/post-tender-award-criteria-lcc.http
   :code:

Успішне додавання критерію LCC:

.. http:example:: http/criteria/lcc-with-valid-award-criteria.http
   :code:
