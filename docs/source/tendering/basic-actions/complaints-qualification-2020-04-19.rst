

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

Complaint Explanations
======================

An explanation of a complaint is a certain textual information and, if necessary, an attached file/files related to a certain complaint and can be used by the AMCU commission during its consideration.
Explanations to the complaint are submitted by subjects on their own initiative, without a request from AMCU. AMCU will not respond to such explanations, but will only consider them.

Once complaint is in `pending` or `accepted` status complaint owner or tender owner can submit a post to complaint as explanation.

Explanations can be added no later than 3 working days before the date of review of the complaint (3 days before reviewDate)

Each explanation must be related to one of the objections of the complaint  (`complaints:objections`).

Complaint owner or tender owner can submit an explanation via `posts`:

.. http:example:: http/complaints/qualification-complaint-post-explanation.http
   :code:

The field `recipient` is forbidden for explanation post:

.. http:example:: http/complaints/qualification-complaint-post-explanation-invalid.http
   :code:

It is forbidden to answer an explanation can submit by setting explanation's post `id` as `relatedPost`:

.. http:example:: http/complaints/qualification-complaint-post-explanation-answer-forbidden.http
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
