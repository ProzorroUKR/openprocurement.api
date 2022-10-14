
.. _bid_requirement_response_operation:

Bid Requirement response
------------------------

Bid requirement response - an object that shows that the user meets the tender owner requirements, and can participate in the procurement.

Any action on the requirement response in the bid can be performed only by the bid owner.

Requirement response basic operation
------------------------------------

Requirement response data :ref:`scheme<RequirementResponse>`

Create Bid Requirement Response
"""""""""""""""""""""""""""""""

You can create few requirement responses in one request with complete set of data.

.. http:example:: http/criteria/create-requirement-response.http
   :code:

You can create requirement responses in one request with bid patch.

.. http:example:: http/criteria/add-requirement-response-from-bid.http
   :code:


Update Bid Requirement Response
"""""""""""""""""""""""""""""""

.. http:example:: http/criteria/update-requirement-response.http
   :code:

You can patch requirement responses in one request with bid patch,
and you must send data about other requirement responses or this other requirement responses will be deleted.

.. http:example:: http/criteria/patch-requirement-response-from-bid.http
   :code:


Get Bid Requirement Response
""""""""""""""""""""""""""""

.. http:example:: http/criteria/requirement-response-list.http
   :code:

.. http:example:: http/criteria/requirement-response.http
   :code:


Delete Requirement Response
"""""""""""""""""""""""""""

.. http:example:: http/criteria/delete-requirement-response.http
   :code:

You can delete requirement responses in one request with bid patch, not send this requirement response data.

.. http:example:: http/criteria/update-requirement-response.http
   :code:


Evidence basic operation
------------------------

Evidence data :ref:`scheme<evidence>`

Create Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/create-requirement-response-evidence.http
   :code:


Update Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/update-requirement-response-evidence.http
   :code:

Get Requirement Response Evidence
"""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/requirement-response-evidence-list.http
   :code:

.. http:example:: http/criteria/requirement-response-evidence.http
   :code:

Delete Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/delete-requirement-response-evidence.http
   :code:

.. _bid_activation_with_requirement_responses:

Bid activation
--------------

When you update bid to `active`/`pending` status or PATCH bid in these statuses, the validation is triggered
that checks the compliance of the responses and criteria requirements.

Responses are necessary only for criteria that have at least one requirement in status "active".

Error when bid doesn't have response for one of criteria:

.. http:example:: http/criteria/requirement-response-basic-data-1.http
   :code:

.. http:example:: http/criteria/bid-activation-not-all-criteria.http
   :code:

Error when bid have responses for few requirement groups inside one criteria:

.. http:example:: http/criteria/requirement-response-basic-data-2.http
   :code:

.. http:example:: http/criteria/bid-activation-answered-on-two-groups.http
   :code:


Error when bid doesn't have all responses for all requirements inside requirement group:

.. http:example:: http/criteria/requirement-response-basic-data-3.http
   :code:

.. http:example:: http/criteria/bid-activation-not-all-requirements.http
   :code:


Workflow Requirement Response
-----------------------------

Workflow of requirement response you could see here: :ref:`Criteria Workflow <criteria_workflow>`