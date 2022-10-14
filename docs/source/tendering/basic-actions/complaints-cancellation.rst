

Complaint Retrieval
===================

Tender Cancellation Complaint Retrieval
---------------------------------------

You can list all Tender Cancellation Complaints:'

.. http:example:: http/complaints/cancellation-complaints-list.http
   :code:

And check individual complaint:

.. http:example:: http/complaints/cancellation-complaint.http
   :code:


Complaint Submission
====================

If tender cancellation are favoriting particular supplier, or in any other viable case, any registered user can submit Tender Cancellation Complaint if tender in `active.tendering` status or participants if tender in any other status.

Tender Cancellation Complaint Submission (with documents)
---------------------------------------------------------

Create complaint for cancellation can anyone if tender has satatus `active.auction` or only bidders in other statuses.

At first create a draft:

.. http:example:: http/complaints/cancellation-complaint-submission.http
   :code:

Then upload necessary documents:

.. http:example:: http/complaints/cancellation-complaint-submission-upload.http
   :code:

Submit tender cancellation complaint:

.. http:example:: http/complaints/cancellation-complaint-complaint.http
   :code:

Tender Cancellation Complaint Submission (without documents)
------------------------------------------------------------

You can submit complaint that does not need additional documents:

.. http:example:: http-outdated/complaints/cancellation-complaint-submission-complaint.http
   :code:


Complaint Resolution
====================

Rejecting Tender Cancellation Complaint
--------------------------------------------------

.. http:example:: http/complaints/cancellation-complaint-reject.http
   :code:


Accepting Tender Cancellation Complaint
--------------------------------------------------

.. http:example:: http/complaints/cancellation-complaint-accept.http
   :code:


Submitting Tender Cancellation Complaint Resolution
---------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. http:example:: http/complaints/cancellation-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. http:example:: http/complaints/cancellation-complaint-resolve.http
   :code:

Or declines it:

.. http:example:: http/complaints/cancellation-complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

For submit resolution confirmation, cancellation must be in `unsuccessful` status.

.. http:example:: http/complaints/cancellation-complaint-resolved.http
   :code:

When the status of cancellation changes to `resolved`, then all terms regarding the tender are recalculated according to the formula:

.. code-block:: python

   period.endDate += complaint.tendererActionDate - cancellation.complaintPeriod.startDate

Cancelling Tender Cancellation Complaint
========================================

Cancelling not accepted complaint
---------------------------------

.. http:example:: http/complaints/cancellation-complaint-reject.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. http:example:: http/complaints/cancellation-complaint-accepted-stopped.http
   :code:
