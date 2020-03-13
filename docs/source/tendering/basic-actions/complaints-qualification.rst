

Claim/Complaint Retrieval
=========================

Tender Qualification Claim/Complaint Retrieval
----------------------------------------------

You can list all Tender Qualification Claims/Complaints:

.. include:: ../http/complaints/qualification-complaints-list.http
   :code:

And check individual complaint:

.. include:: ../http/complaints/qualification-complaint.http
   :code:

Complaint Submission
====================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Complaint.

Tender Qualification Complaint Submission (with documents)
----------------------------------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. include:: ../http/complaints/qualification-complaint-submission.http
   :code:

Then upload necessary documents:
   
.. include:: ../http/complaints/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification complaint:
   
.. include:: ../http/complaints/qualification-complaint-complaint.http
   :code:

Tender Qualification Complaint Submission (without documents)
-------------------------------------------------------------

You can submit complaint that does not need additional documents:

.. include:: ../http/complaints/qualification-complaint-submission-complaint.http
   :code:

Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. include:: ../http/complaints/qualification-complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: ../http/complaints/qualification-complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. include:: ../http/complaints/qualification-complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: ../http/complaints/qualification-complaint-post-tender-owner.http
   :code:


Complaint Resolution
====================

Rejecting Tender Qualification Complaint
----------------------------------------

.. include:: ../http/complaints/qualification-complaint-reject.http
   :code:


Accepting Tender Qualification Complaint
----------------------------------------

.. include:: ../http/complaints/qualification-complaint-accept.http
   :code:


Submitting Tender Qualification Complaint Resolution
----------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: ../http/complaints/qualification-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: ../http/complaints/qualification-complaint-resolve.http
   :code:

Or declines it:

.. include:: ../http/complaints/qualification-complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. include:: ../http/complaints/qualification-complaint-resolved.http
   :code:

Cancelling Tender Qualification Complaint
=========================================

Cancelling not accepted complaint
---------------------------------

.. include:: ../http/complaints/qualification-complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: ../http/complaints/qualification-complaint-accepted-stopping.http
   :code:

.. include:: ../http/complaints/qualification-complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: ../http/complaints/qualification-complaint-accepted-stopped.http
   :code:
