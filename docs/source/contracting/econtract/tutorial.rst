.. _econtracting_tutorial:

Tutorial
========

Загальна картина
----------------

Процес визначення переможця відбувається на майданчиках 1-4 рівнів акредитації.

Процес електронного контракту відбувається на майданчиках 6 рівня акредитації.

.. image:: /contracting/econtract/diagram/activity/image.png

Передумови
----------

Вимоги до тендеру
~~~~~~~~~~~~~~~~~

Для електронних контрактів тендер має відповідати наступним вимогам

* має бути обрано шаблон договору за допомогою поля `contractTemplateName` в тендері
* має бути обраним майданчик 6 рівня акредитації для замовників та постачальників

Розглянемо детальніше вимоги щодо тендеру.

Шаблон договору
~~~~~~~~~~~~~~~

Поле `contractTemplateName` має бути обов'язково обрано на етапі створення тендеру (більше тут :ref:`contract-template-name`)

Це поле визначає шаблон договору, який буде використано для створення PDF документу договору.

Майданчик 6 рівня акредитації
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

При створенні контракту замовнику (buyer) та постачальнику (supplier) має бути надано можливість вказати майданчик на якому буде проходити контрактінг.

Назва майданчика має бути вказана

* в полі `contract_owner` в `procuringEntity` (або `buyers` для закупівель ЦЗО) для замовників
* в полі `contract_owner` в `tenderers` пропозиції для постачальників

Поле `contract_owner` може мати лише назву майданчика, який пройшов акредитацію 6 рівня.

Для замовника майданчик має вказати поле `contract_owner` в `procuringEntity` (або `buyers` для закупівель ЦЗО).

Отримати перелік майданчиків можна за допомогою API запиту:

.. http:example:: http/get-brokers-all.http
   :code:

Якщо спробувати створити тендер з майданчиком не 6го рівня, то отримаємо помилку:

.. http:example:: http/create-tender-broker-1-fail.http
   :code:

Відфільтруємо майданчики 6го рівня:

.. http:example:: http/get-brokers-level-6.http
   :code:

Створимо тендер з майданчиком 6го рівня:

.. http:example:: http/create-tender-broker-6.http
   :code:

Тендер створено успішно.

Для постачальника майданчик має вказати поле `contract_owner` в полі `tenderers` пропозиції.

Переглянемо як виглядає пропозиція для постачальника:

.. http:example:: http/get-bid.http
   :code:

Як бачимо, майданчик вказано правильно.

Creating contract
-----------------

Let's say that we have conducted tender with award. When the award is activated, a contract is **automatically** created in the tender with a limited set of fields(`id`, `awardID`, `status`, `date`, `value`) and in the contracting module with a full set of fields(:ref:`Econtract`) in ``pending`` status.

A contract is created with additional fields:

* `contractTemplateName` - copied from tender if exists (more about it in :ref:`contract-template-name`)
* `period` - `startDate` equals `dateCreated` + 5 calendar days, `endDate` is the end of the year of `startDate`

A PQ contract is created with additional fields:

* `attributes` - formed from requirements and responses in tender

Also, PDF document is created based on the template (`contractTemplateName`) and automatically attached to the contract with documentType `contractNotice`. 

This document will be required for signing for both supplier and buyer later to activate the contract.

Getting contract
----------------

Contract in the tender system

.. http:example:: http/example-contract.http
   :code:

*Contract id is the same in both tender and contract system.*

Let’s see what listing of contracts in contracting module reveals us:

.. http:example:: http/contract-list.http
   :code:



Let's access the URL of the created object:

.. http:example:: http/contract-view.http
   :code:

Getting access
---------------

For getting access for buyer or supplier endpoint `contracts/{contract_id}/access` is used after contract was created.

Algorith of getting access:

* POST `/access` with identifier of client - returns token for client

Main action is POST `/access` - a query with a client identifier determines whether it is a buyer or supplier.
If the identifier does not match any of the entities, an error is issued:

.. http:example:: http/contract-access-invalid.http
   :code:

If identifier is found, then we validate whether authenticated user is an owner for this role:

.. http:example:: http/contract-access-owner-invalid.http
   :code:

If identifier is found and owner matches, then the token is set according to the entity for supplier or buyer:

.. http:example:: http/contract-access-by-buyer.http
   :code:

If buyer get access, we will see in response new `transfer` token too.

After token generation, it is allowed to regenerate token, make new POST request with this identifier:

.. http:example:: http/contract-access-by-buyer-2.http
   :code:

**NOTE:**
Then user can modify contract as buyer only using the last generated token.

After token was regenerated, previous token can not be used for updating contract:

.. http:example:: http/contract-patch-by-buyer-1-forbidden.http
   :code:

The same algorithm will be for supplier access.

Let's require access for supplier:

.. http:example:: http/contract-access-by-supplier.http
   :code:

**WARNING:**
It is allowed to get access only during contract is `pending`.

Activating contract
-------------------

If contract was created using new flow with set `contract_owner` in tender for `suppliers` and `buyers` than for activating electronic contract, signer information and all participants signature are required.

To activate contract it is required to add contract signature document type from each participant (supplier and buyer).

Requirements for signing:

* Contract document with documentType `contractNotice` should be signed
* Signature file should be attached to the contract with documentType `contractSignature`
* Signature must have following parameters:

  * Format: CAdES-X Long
  * Algorithm: DSTU 4145
  * Type: Separate data and signature files (detached)

Here is a diagram of the signing process:

.. image:: /contracting/econtract/diagram/e_contract_pdf_signing/image.png

If both sides signed the current version of contract, than contract becomes `active`.

Supplier adds signature document using his token (`supplier_token`) which he got during access query:

.. http:example:: http/contract-supplier-add-signature-doc.http
   :code:

Buyer adds signature document using his token (`buyer_token`) which he got during access query:

.. http:example:: http/contract-buyer-add-signature-doc.http
   :code:

If all required signatures are completed, the contract will automatically transition to the `active` status:

.. http:example:: http/get-active-contract.http
   :code:


.. _contract_versions:

New versions of contract
=========================

If one of sides doesn't agree to sign current version of contract, there is an opportunity to create a new version of contract.

Flow:

* create a cancellation of current version of contract

* POST new version o contract with updates

* sign new version and wait till another side agrees to sign (or create new version by his side)

Cancellations
--------------

It is allowed to cancel current version of contract and create new one during contract is `pending`.

To cancel current version of contract, participant of contract should create a cancellation with reason `requiresChanges`:

.. http:example:: http/contract-supplier-cancels-contract.http
   :code:

Let's look at contract:

.. http:example:: http/cancellation-of-contract.http
   :code:

It is forbidden to add more than one cancellation:

.. http:example:: http/cancellation-of-contract-duplicated.http
   :code:

After cancellation created, there is forbidden to sign contract:

.. http:example:: http/contract-supplier-add-signature-forbidden.http
   :code:

Create new contract version
---------------------------

Then any of the participant should create a new version of contract using his token.

Allowed fields for updating:

* period
* contractNumber
* items.unit
* items.quantity
* value
* title
* title_en
* description
* description_en
* dateSigned
* signerInfo (for supplier or buyer depends on who cancelled contract)
* milestones

If participant tried to update another field, he will see an error:

.. http:example:: http/contract-supplier-post-contract-invalid.http
   :code:

Let's update fields `period` and `signerInfo.name` using token for supplier:

.. http:example:: http/contract-supplier-post-contract-version.http
   :code:

Success! Let's look at previous version of contract, it became `cancelled` and cancellation now is `active`:

.. http:example:: http/get-previous-contract-version.http
   :code:

Let's look at all contracts in tender:

.. http:example:: http/get-tender-contracts.http
   :code:

After that new round of signatures begins.

Supplier and buyer can sign this new version of contract if they agreed with changes or create new version if disagreed.

Cancellations of Econtract
===========================

It is allowed to cancel contract while it is on `pending` status.

There are two `reasonTypes` for creating cancellation of contract:

* `requiresChanges`
* `signingRefusal`

Reason `requiresChanges` means that one of the sides doesn't agree to sign current version of contract, and they want to create a new version of contract. Described in :ref:`contract_versions`.

Reason `signingRefusal` means that the winner of tender is refused to sign aa contract, that's why his award should be cancelled by buyer.

Participant of contract can create a cancellation with reason `signingRefusal`:

.. http:example:: http/contract-supplier-cancels-contract-2.http
   :code:

Let's look at contract:

.. http:example:: http/winner-cancellation-of-contract.http
   :code:

After that buyer should cancel the winner via award:

.. http:example:: http/winner-award-cancellation.http
   :code:

Let's look at contract one more time and we will see that contract became `cancelled`, cancellation became `active`:

.. http:example:: http/contract-with-winner-cancellation.http
   :code:

Let's look at tender, the winner is cancelled an awarding is continuing:

.. http:example:: http/tender-with-winner-cancellation-of-contract.http
   :code:

Changes for active contract
=============================

Changes to the terms of the contracts can be made by the signatories through the submission and signing of an additional agreement. The system uses the terminology "changes".

The initiator of the change can be both the buyer and the supplier.

The initiator fills in three mandatory fields:

:rationale:
    string, reason of changes

:rationaleTypes:
    list, reason type of changes

    Possible values for field `rationaleTypes` are validated from list of keys in `contractChangeRationaleTypes`.

:modifications:
    object, new values in fields


`modifications` is a structure that reflects the changes in the contract field that will be made:

:title:
    string

:title_en:
    string

:description:
    string

:description_en:
    string

:period:
    :ref:`Period`

    The start and end date for the contract.

:items:
    List of :ref:`Item` objects

:value:
    :ref:`ContractValue` object

:contractNumber:
    string

:milestones:
    List of :ref:`ContractMilestone` objects

Changes can be made only to signed contracts:

.. http:example:: http/changes-for-pending-contract.http
   :code:

Creating changes
------------------

If we set `rationaleTypes` not from `contractChangeRationaleTypes` we will see an error:

.. http:example:: http/create-change-invalid-rationale-types.http
   :code:

Request to create a change:

.. http:example:: http/create-change.http
   :code:

There are validations for some fields during changes.

For example, if the buyer decided to change currency in contract value:

.. http:example:: http/change-modifications-invalid-currency.http
   :code:

For example, if the supplier decided to change period endDate in contract to incorrect date:

.. http:example:: http/change-modifications-invalid-period.http
   :code:

Change activation
------------------

To activate change it is required to add contract signature document type from each participant (supplier and buyer).

If both sides signed the current version of change, than change becomes `active` and modifications will be taken into account during next changes.

Supplier adds signature document using his token (`supplier_token`):

.. http:example:: http/change-supplier-add-signature-doc.http
   :code:

Buyer adds signature document using his token (`buyer_token`):

.. http:example:: http/change-buyer-add-signature-doc.http
   :code:

If all required signatures are completed, the change will automatically transition to the `active` status:

.. http:example:: http/get-active-change.http
   :code:

Cancellations
--------------

It is allowed to cancel change of contract if it is not actual anymore.

Create one more change:

.. http:example:: http/create-change-2.http
   :code:

To cancel change, participant of contract should create a cancellation with reason:

.. http:example:: http/contract-supplier-cancels-change.http
   :code:

Let's look at change:

.. http:example:: http/cancellation-of-change.http
   :code:

It is forbidden to add more than one cancellation:

.. http:example:: http/cancellation-of-change-duplicated.http
   :code:

After cancellation created, there is forbidden to sign change:

.. http:example:: http/contract-supplier-add-signature-to-change-forbidden.http
    :code:

Signing additional changes does not change the electronic fields of the contract itself.
That is, if, for example, the value of the contract was changed by an additional change, then changes will contain the current value, and the contract will contain the value current at the time of signing the contract:

.. http:example:: http/get-contract-with-changes.http
    :code:

Items length change
--------------------

There is an opportunity to change length of items during contract is `active` using `changes`.

It is allowed to add new items, but the main fields should be the same as in one of previous item in contact.

Fields that can not be changed:

* `classification`
* `relatedLot`
* `relatedBuyer`
* `additionalClassifications`

Let's try to add new item with new `classification` and we will see an error:

.. http:example:: http/create-change-items-invalid-classification.http
    :code:

For example, we can split first item into two new items.

But there is still a validation for unit prices of all items:

.. http:example:: http/create-change-items-invalid-price.http
    :code:

Let's update quantity in first item and add new item with correct `unit.value`:

.. http:example:: http/create-change-items.http
    :code:
