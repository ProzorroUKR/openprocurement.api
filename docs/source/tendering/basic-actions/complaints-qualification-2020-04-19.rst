

Claim/Complaint Retrieval
=========================

Tender Qualification Claim/Complaint Retrieval
----------------------------------------------

You can list all Tender Qualification Claims/Complaints:

.. http:example:: http/complaints/qualification-complaints-list.http
   :code:

And check individual complaint:

.. http:example:: http/complaints/qualification-complaint.http
   :code:

Complaint Submission
====================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Complaint.

Tender Qualification Complaint Submission
-----------------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. http:example:: http/complaints/qualification-complaint-submission.http
   :code:

When creating a complaint, the User can add one or more Objections raised by the Complainant as part of the complaint.
Objections can be added or edited while complaint is in the status `draft`.
For more details, see :ref:`tender complaint objections <complaint-objections>`.

This step is optional. Upload documents:

.. http:example:: http/complaints/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification complaint:

.. http:example:: http/complaints/qualification-complaint-complaint.http
   :code:


Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. http:example:: http/complaints/qualification-complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. http:example:: http/complaints/qualification-complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. http:example:: http/complaints/qualification-complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. http:example:: http/complaints/qualification-complaint-post-tender-owner.http
   :code:


Complaint Resolution
====================

Rejecting Tender Qualification Complaint
----------------------------------------

.. http:example:: http/complaints/qualification-complaint-reject.http
   :code:


Accepting Tender Qualification Complaint
----------------------------------------

.. http:example:: http/complaints/qualification-complaint-accept.http
   :code:


Submitting Tender Qualification Complaint Resolution
----------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. http:example:: http/complaints/qualification-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. http:example:: http/complaints/qualification-complaint-resolve.http
   :code:

Or declines it:

.. http:example:: http/complaints/qualification-complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. http:example:: http/complaints/qualification-complaint-resolved.http
   :code:

Cancelling Tender Qualification Complaint
=========================================

Cancelling draft complaint by Complainant
-----------------------------------------

.. http:example:: http/complaints/qualification-complaint-mistaken.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. http:example:: http/complaints/qualification-complaint-accepted-stopped.http
   :code:
