

Claim/Complaint Retrieval
=========================

Tender Conditions Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Conditions Claims/Complaints:

.. include:: ../http/complaints/complaints-list.http
   :code:

And check individual complaint or claim:

.. include:: ../http/complaints/complaint.http
   :code:


Complaint Submission
====================

If tender conditions are favoriting particular supplier, or in any other viable case, any registered user can submit Tender Conditions Complaint.


Tender Conditions Complaint Submission
--------------------------------------

At first create a draft:

.. include:: ../http/complaints/complaint-submission.http
   :code:

This step is optional. Upload documents:

.. include:: ../http/complaints/complaint-submission-upload.http
   :code:

Submit tender conditions complaint:

.. include:: ../http/complaints/complaint-complaint.http
   :code:


Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. include:: ../http/complaints/complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: ../http/complaints/complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. include:: ../http/complaints/complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: ../http/complaints/complaint-post-tender-owner.http
   :code:


Complaint Resolution
====================

Rejecting Tender Conditions Complaint
-------------------------------------

.. include:: ../http/complaints/complaint-reject.http
   :code:


Accepting Tender Conditions Complaint
-------------------------------------

.. include:: ../http/complaints/complaint-accept.http
   :code:


Submitting Tender Conditions Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: ../http/complaints/complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: ../http/complaints/complaint-resolve.http
   :code:

Or declines it:

.. include:: ../http/complaints/complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. include:: ../http/complaints/complaint-resolved.http
   :code:

Cancelling Tender Conditions Complaint
======================================

Cancelling not accepted complaint
---------------------------------

.. include:: ../http/complaints/complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: ../http/complaints/complaint-accepted-stopping.http
   :code:

.. include:: ../http/complaints/complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: ../http/complaints/complaint-accepted-stopped.http
   :code:
