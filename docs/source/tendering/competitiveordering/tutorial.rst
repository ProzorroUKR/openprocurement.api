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

Creating tender
---------------

Tender `competitiveOrdering` has pre-selection procedure and has to be connected to agreement.

Let's use next agreement for our example:

.. http:example:: http/view-agreement-1-contract.http
   :code:

We can create tender connected to this agreement:

.. http:example:: http/tender-post-attempt-json-data.http
   :code:

Tender can contain only one lot. If we will try to add more than one lot, we will get error:

.. http:example:: http/tender-add-lot-more-than-1-error.http
   :code:

Also you will need to update data about item's related lots:

.. http:example:: http/tender-add-relatedLot-to-item.http
   :code:

Tender activating
-----------------

At first we needed to add EXCLUSION criteria to our tender(:ref:`About criteria you can read here<criteria_operation>`).

.. http:example:: http/add-exclusion-criteria.http
   :code:

Let's try to activate tender:

.. http:example:: http/tender-activating-insufficient-active-contracts-error.http
   :code:

You can see that we got error, because we have not enough active contracts in our agreement.

There is the list of all validation errors that can be raised during tender activation related to agreement:

* agreement[0] not found in agreements"
* agreements[0] status is not active"
* agreements[0] has less than 3 active contracts"
* tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)

After adding more active contracts to our agreement let's make another attempt to activate tender:

.. http:example:: http/tender-activating.http
   :code:

You can see that tender was activated successfully.

.. note::
    Further steps for `competitiveOrdering` tender are the same as in :ref:`open`, you can follow corresponding tutorial :ref:`open_tutorial`.
