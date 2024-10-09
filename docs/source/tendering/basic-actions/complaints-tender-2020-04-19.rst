

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


Tender Conditions Complaint Submission
--------------------------------------

At first create a draft:

.. http:example:: http/complaints/complaint-submission.http
   :code:

This step is optional. Upload documents:

.. http:example:: http/complaints/complaint-submission-upload.http
   :code:

Submit tender conditions complaint:

.. http:example:: http/complaints/complaint-complaint.http
   :code:


.. _complaint-objections:

Complaint Objections
====================

When creating a complaint, the User can add one or more Objections raised by the Complainant as part of the complaint:

.. http:example:: http/complaints/complaint-objections-submission.http
   :code:

Objections can be added or edited while complaint is in the status `draft`.

For each Objection, the Complainant must indicate one or more arguments. In other case there error will be raised:

.. http:example:: http/complaints/complaint-objections-invalid-arguments.http
   :code:

For each Arguments, the Complainant can indicate one or more evidences. Evidences can be empty:

.. http:example:: http/complaints/complaint-objections-empty-evidences.http
   :code:

During adding evidence, the User must indicate related document id. This document should be uploaded to complaint.
Let's upload document to complaint:

.. http:example:: http/complaints/complaint-document-upload.http
   :code:

After that User can indicate relatedDocument in evidence:

.. http:example:: http/complaints/complaint-objections-evidences-with-document.http
   :code:

There is an opportunity to create complaint already with document which can be used as relatedDocument in evidences:

.. http:example:: http/complaints/complaint-objections-with-document-one-action.http
   :code:

For each Objection, the Complainant must specify one or more requestedRemedies. In other case there error will be raised:

.. http:example:: http/complaints/complaint-objections-invalid-requested-remedies.http
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

Complaint Explanations
======================

An explanation of a complaint is a certain textual information and, if necessary, an attached file/files related to a certain complaint and can be used by the AMCU commission during its consideration.
Explanations to the complaint are submitted by subjects on their own initiative, without a request from AMCU. AMCU will not respond to such explanations, but will only consider them.

Once complaint is in `pending` or `accepted` status complaint owner or tender owner can submit a post to complaint as explanation.

Explanations can be added no later than 3 working days before the date of review of the complaint (3 days before reviewDate)

Each explanation must be related to one of the objections of the complaint  (`complaints:objections`).

Complaint owner or tender owner can submit an explanation via `posts`:

.. http:example:: http/complaints/complaint-post-explanation.http
   :code:

The field `recipient` is forbidden for explanation post:

.. http:example:: http/complaints/complaint-post-explanation-invalid.http
   :code:

It is forbidden to answer an explanation can submit by setting explanation's post `id` as `relatedPost`:

.. http:example:: http/complaints/complaint-post-explanation-answer-forbidden.http
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

Cancelling draft complaint by Complainant
-----------------------------------------

.. http:example:: http/complaints/complaint-mistaken.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. http:example:: http/complaints/complaint-accepted-stopped.http
   :code:
