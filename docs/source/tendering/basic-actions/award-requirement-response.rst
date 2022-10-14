
.. _award_requirement_response_operation:

Award Requirement response
--------------------------

Any action on the requirement response in the award can be performed only by the tender owner.

Requirement response basic operation
------------------------------------

Requirement response data :ref:`scheme<RequirementResponse>`


Create Award Requirement Response
"""""""""""""""""""""""""""""""""

You can create few requirement responses in one request with complete set of data.

.. http:example:: http/criteria/award-create-requirement-response.http
   :code:

You can create requirement responses in one request with award patch.

.. http:example:: http/criteria/add-requirement-response-from-award.http
   :code:


Update Award Requirement Response
"""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/award-update-requirement-response.http
   :code:

You can patch requirement responses in one request with award patch,
and you must send data about other requirement responses or this other requirement responses will be deleted.

.. http:example:: http/criteria/patch-requirement-response-from-award.http
   :code:


Get Award Requirement Response
""""""""""""""""""""""""""""""

.. http:example:: http/criteria/award-requirement-response-list.http
   :code:

.. http:example:: http/criteria/award-requirement-response.http
   :code:


Delete Requirement Response
"""""""""""""""""""""""""""

.. http:example:: http/criteria/award-delete-requirement-response.http
   :code:

You can delete requirement responses in one request with award patch, not send this requirement response data.

.. http:example:: http/criteria/award-update-requirement-response.http
   :code:


Evidence basic operation
------------------------

Evidence data :ref:`scheme<evidence>`

Create Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/award-create-requirement-response-evidence.http
   :code:


Update Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/award-update-requirement-response-evidence.http
   :code:

Get Requirement Response Evidence
"""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/award-requirement-response-evidence-list.http
   :code:

.. http:example:: http/criteria/award-requirement-response-evidence.http
   :code:

Delete Requirement Response Evidence
""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/award-delete-requirement-response-evidence.http
   :code:
