.. _agreement_cfaua_tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/agreements` endpoint:

.. http:example:: http/agreements-listing-0.http
   :code:

Just invoking it reveals an empty set.

Agreement is transferred from the tender system by an automated process.


.. index:: Agreements

Creating agreement
------------------

Let's say that we have conducted tender and it has ``complete`` status. When the tender is completed, agreement (that has been created in the tender system) is transferred to the agreement system **automatically**.

*Brokers (eMalls) can't create agreements in the agreement system.*

Getting agreement
-----------------

Agreement in the tender system

.. http:example:: http/example_agreement.http
   :code:

*Agreement id is the same in both tender and agreement system.*

Let's access the URL of the created object inside agreement system:

.. http:example:: http/agreement-view.http
   :code:

Getting access
--------------

In order to get rights for future agreement editing, you need to use this view ``PATCH: /agreements/{id}/credentials?acc_token={tender_token}`` with the API key of the eMall (broker), where tender was generated.

In the ``PATCH: /agreements/{id}/credentials?acc_token={tender_token}``:

* ``id`` stands for agreement id,

* ``tender_token`` is tender's token (is used for agreement token generation).

Response will contain ``access.token`` for the agreement that can be used for further agreement modification.

.. http:example:: http/agreement-credentials.http
   :code:

Let's view agreements.

.. http:example:: http/agreements-listing-1.http
   :code:


We do see the internal `id` of a agreement (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/agreements/`) and its `dateModified` datestamp.


Modifying agreement
-------------------


**Essential agreement terms** can be modified by the submission of a new `change` object to the `Agreement.changes` container. `Change` can be one of this types :ref:`ChangeTaxRate`, :ref:`ChangeItemPriceVariation`, :ref:`ChangePartyWithdrawal` or :ref:`ChangeThirdParty`

All `changes` are processed by the endpoint `/agreement/{id}/changes`.

Submitting a change
~~~~~~~~~~~~~~~~~~~

Let's add new `change` to the agreement:

.. http:example:: http/add-agreement-change.http
   :code:

Note that you should provide value in ``rationaleType`` field. This field is required.

You can view the `change`:

.. http:example:: http/view-agreement-change.http
   :code:

`Change` can be modified while it is in the ``pending`` status:

.. http:example:: http/patch-agreement-change.http
   :code:

Uploading change document
~~~~~~~~~~~~~~~~~~~~~~~~~

Document can be added only while `change` is in the ``pending`` status.

Document has to be added in two stages:

* you should upload document

.. http:example:: http/add-agreement-change-document.http
   :code:

* you should set document properties ``"documentOf": "change"`` and ``"relatedItem": "{change.id}"`` in order to bind the uploaded document to the `change`:

.. http:example:: http/set-document-of-change.http
   :code:

Updating agreement properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you can update agreement properties which belong to the change.

.. http:example:: http/add-agreement-change-modification.http
   :code:

In case of multiple :ref:`Item` you are allowed to change in `modifications` each `factor`.

Agreement preview
~~~~~~~~~~~~~~~~~

Also, while `change` is in the ``pending`` status, you can see agreement as `change` would be applied.
You need to use this view ``GET: /agreements/{id}/preview?acc_token={agreement_token}``.

.. http:example:: http/agreement_preview.http
   :code:

As you can see, `value.amount` on `contracts` `unitPrices` are changed due `modification` is applied. So if this `modification` is what you need, you can apply `change`.

Applying the change
~~~~~~~~~~~~~~~~~~~

`Change` can be applied by switching to the ``active`` status.

In order to apply ``active`` status `dateSigned` field must be set.

After this `change` can't be modified anymore.

.. http:example:: http/apply-agreement-change.http
   :code:

`dateSigned` field validation:

* for the first agreement `change` date should be after `agreement.dateSigned`;

* for all next `change` objects date should be after the previous `change.dateSigned`.

You can view all changes:

.. http:example:: http/view-all-agreement-changes.http
   :code:

All changes are also listed on the agreement view.

.. http:example:: http/view-agreement.http
   :code:

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created agreement. Uploading should
follow the `upload` rules.

.. http:example:: http/upload-agreement-document.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: http/agreement-documents.http
   :code:

And again we can confirm that there are two documents uploaded.

.. http:example:: http/upload-agreement-document-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. http:example:: http/upload-agreement-document-3.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: http/get-agreement-document-3.http
   :code:


.. index:: Enquiries, Question, Answer


Completing agreement
--------------------

Agreement can be completed by switching to ``terminated`` status.
Let's perform these actions in single request:

.. http:example:: http/agreement-termination.http
   :code:

If agreement is unsuccessful reasons for termination ``terminationDetails`` should be specified.

Any future modification to the agreement are not allowed.


It may be useful to see top requirements: `Test Cases for III level of accreditation <https://docs.google.com/spreadsheets/d/1-AT2RjbnSFAP75x6YNDvhKeN2Cy3tMlG6kb0tt6FScs/edit#gid=0>`_ and
`Test Cases for IV level of accreditation <https://docs.google.com/spreadsheets/d/1-93kcQ2EeuUU08aqPMDwMeAjnG2SGnEEh5RtjHWOlOY/edit#gid=0>`_.
