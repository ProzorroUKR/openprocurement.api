

Claim/Complaint Retrieval
=========================

Tender Conditions Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Conditions Claims/Complaints:

.. http:example:: http/complaints/complaints-list.http
   :code:

And check individual complaint or claim:

.. http:example:: http/complaints/complaint.http
   :code:


Complaint Submission
====================

If tender conditions are favoriting particular supplier, or in any other viable case, any registered user can submit Tender Conditions Complaint.


Tender Conditions Complaint Submission (with documents)
-------------------------------------------------------

At first create a draft:

.. http:example:: http/complaints/complaint-submission.http
   :code:

Then upload necessary documents:
   
.. http:example:: http/complaints/complaint-submission-upload.http
   :code:

Submit tender conditions complaint:
   
.. http:example:: http/complaints/complaint-complaint.http
   :code:

Tender Conditions Complaint Submission (without documents)
----------------------------------------------------------

You can submit complaint that does not need additional documents:

.. http:example:: http-outdated/complaints/complaint-submission-complaint.http
   :code:

Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. http:example:: http/complaints/complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. http:example:: http/complaints/complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. http:example:: http/complaints/complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. http:example:: http/complaints/complaint-post-tender-owner.http
   :code:


Complaint Resolution
====================

Rejecting Tender Conditions Complaint
-------------------------------------

.. http:example:: http/complaints/complaint-reject.http
   :code:


Accepting Tender Conditions Complaint
-------------------------------------

.. http:example:: http/complaints/complaint-accept.http
   :code:


Submitting Tender Conditions Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. http:example:: http/complaints/complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. http:example:: http/complaints/complaint-resolve.http
   :code:

Or declines it:

.. http:example:: http/complaints/complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. http:example:: http/complaints/complaint-resolved.http
   :code:

Cancelling Tender Conditions Complaint
======================================

Cancelling not accepted(pending) complaint by Reviewer
------------------------------------------------------

.. http:example:: http-outdated/complaints/complaint-mistaken.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. http:example:: http-outdated/complaints/complaint-accepted-stopping.http
   :code:

.. http:example:: http-outdated/complaints/complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. http:example:: http/complaints/complaint-accepted-stopped.http
   :code:
