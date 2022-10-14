
.. _qualification_requirement_response_operation:

Qualification Requirement response
----------------------------------

Any action on the requirement response in the award can be performed only by the tender owner.

Requirement response basic operation
------------------------------------

Requirement response data :ref:`scheme<RequirementResponse>`


Create Qualification Requirement Response
"""""""""""""""""""""""""""""""""""""""""

You can create few requirement responses in one request with complete set of data.

.. http:example:: http/criteria/qualification-create-requirement-response.http
   :code:

You can create requirement responses in one request with qualification patch.

.. http:example:: http/criteria/add-requirement-response-from-qualification.http
   :code:


Update Qualification Requirement Response
"""""""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-update-requirement-response.http
   :code:

You can patch requirement responses in one request with qualification patch,
and you must send data about other requirement responses or this other requirement responses will be deleted.

.. http:example:: http/criteria/patch-requirement-response-from-qualification.http
   :code:


Get Qualification Requirement Response
""""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-requirement-response-list.http
   :code:

.. http:example:: http/criteria/qualification-requirement-response.http
   :code:


Delete Requirement Response
"""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-delete-requirement-response.http
   :code:

You can delete requirement responses in one request with qualification patch, not send this requirement response data.

.. http:example:: http/criteria/qualification-update-requirement-response.http
   :code:


Evidence basic operation
------------------------

Evidence data :ref:`scheme<evidence>`

Create Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-create-requirement-response-evidence.http
   :code:


Update Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-update-requirement-response-evidence.http
   :code:

Get Requirement Response Evidence
"""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-requirement-response-evidence-list.http
   :code:

.. http:example:: http/criteria/qualification-requirement-response-evidence.http
   :code:

Delete Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-delete-requirement-response-evidence.http
   :code:
