
.. _bid_requirement_response_operation:

Bid Requirement response
========================

Bid requirement response - an object that shows that the user meets the tender owner requirements, and can participate in the procurement.

Any action on the requirement response in the bid can be performed only by the bid owner.

Requirement response basic operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requirement response data :ref:`scheme<RequirementResponse>`

Create Bid Requirement Response
"""""""""""""""""""""""""""""""

You can create few requirement responses in one request with complete set of data.

.. include:: ../http/criteria/create-requirement-response.http
   :code:


Update Bid Requirement Response
"""""""""""""""""""""""""""""""

.. include:: ../http/criteria/update-requirement-response.http
   :code:


Get Bid Requirement Response
""""""""""""""""""""""""""""

.. include:: ../http/criteria/requirement-response-list.http
   :code:

.. include:: ../http/criteria/requirement-response.http
   :code:


Delete Requirement Response
"""""""""""""""""""""""""""

.. include:: ../http/criteria/delete-requirement-response.http
   :code:


Evidence basic operation
~~~~~~~~~~~~~~~~~~~~~~~~

Evidence data :ref:`scheme<evidence>`

Create Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. include:: ../http/criteria/create-requirement-response-evidence.http
   :code:


Update Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. include:: ../http/criteria/update-requirement-response-evidence.http
   :code:

Get Requirement Response Evidence
"""""""""""""""""""""""""""""""""

.. include:: ../http/criteria/requirement-response-evidence-list.http
   :code:

.. include:: ../http/criteria/requirement-response-evidence.http
   :code:

Delete Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. include:: ../http/criteria/delete-requirement-response-evidence.http
   :code:


Workflow Requirement Response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Workflow of requirement response you could see here: :ref:`Criteria Workflow <criteria_workflow>`