

Claim/Complaint Retrieval
=========================

Tender Award Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Award Claims/Complaints:

.. http:example:: http/complaints/award-complaints-list.http
   :code:

And check individual complaint:

.. http:example:: http/complaints/award-complaint.http
   :code:

Complaint Submission
====================

If tender award is favoriting certain supplier, or in any other viable case, participants who were admitted to auction can submit Tender Award Complaint.

Tender Award Complaint Submission for unsuccessful award
---------------------------------------------------------

For unsuccessful award it is allowed only that bidder of award can complain on his award.

Let's try to complain to unsuccessful award from another bidder and we will see an error:

.. http:example:: http/complaints/award-unsuccessful-complaint-invalid-bidder.http
   :code:

Now let's make a complain from correct bidder:

.. http:example:: http/complaints/award-unsuccessful-complaint-valid-bidder.http
   :code:


Tender Award Complaint Submission for the winner
------------------------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. http:example:: http/complaints/award-complaint-submission.http
   :code:

When creating a complaint, the User can add one or more Objections raised by the Complainant as part of the complaint.
Objections can be added or edited while complaint is in the status `draft`.
For more details, see :ref:`tender complaint objections <complaint-objections>`.

This step is optional. Upload documents:

.. http:example:: http/complaints/award-complaint-submission-upload.http
   :code:

Submit tender award complaint:

.. http:example:: http/complaints/award-complaint-complaint.http
   :code:


Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. http:example:: http/complaints/award-complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. http:example:: http/complaints/award-complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. http:example:: http/complaints/award-complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. http:example:: http/complaints/award-complaint-post-tender-owner.http
   :code:

Complaint Appeals
==================

Once complaint is in `invalid`, `satisfied`, `declined` or `resolved` status tender owner or complaint author can submit an appeal for complaint.

For more details, see :ref:`tender complaint appeals <complaint-appeals>`.

Complaint Explanations
======================

An explanation of a complaint is a certain textual information and, if necessary, an attached file/files related to a certain complaint and can be used by the AMCU commission during its consideration.
Explanations to the complaint are submitted by subjects on their own initiative, without a request from AMCU. AMCU will not respond to such explanations, but will only consider them.

Once complaint is in `pending` or `accepted` status complaint owner or tender owner can submit a post to complaint as explanation.

Explanations can be added no later than 3 working days before the date of review of the complaint (3 days before reviewDate)

Each explanation must be related to one of the objections of the complaint  (`complaints:objections`).

Complaint owner or tender owner can submit an explanation via `posts`:

.. http:example:: http/complaints/award-complaint-post-explanation.http
   :code:

The field `recipient` is forbidden for explanation post:

.. http:example:: http/complaints/award-complaint-post-explanation-invalid.http
   :code:

It is forbidden to answer an explanation can submit by setting explanation's post `id` as `relatedPost`:

.. http:example:: http/complaints/award-complaint-post-explanation-answer-forbidden.http
   :code:

Complaint Resolution
====================

Rejecting Tender Award Complaint
-------------------------------------

.. http:example:: http/complaints/award-complaint-reject.http
   :code:


Accepting Tender Award Complaint
-------------------------------------

.. http:example:: http/complaints/award-complaint-accept.http
   :code:


Submitting Tender Award Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. http:example:: http/complaints/award-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. http:example:: http/complaints/award-complaint-resolve.http
   :code:

Or declines it:

.. http:example:: http/complaints/award-complaint-decline.http
   :code:

Correcting problems
-------------------

If tender award complaint was satisfied by the Complaint Review Body, then procuring entity has to correct problems.

One of the possible solutions is award cancellation:


.. http:example:: http/complaints/award-complaint-satisfied-resolving.http
   :code:

After award cancellation system generates new award. Its location is present in the `Location` header of response.

Submitting Resolution Confirmation
----------------------------------
When complaint has been successfully resolved, procuring entity submits resolution confirmation.

.. http:example:: http/complaints/award-complaint-resolved.http
   :code:

Submitting complaint to new award
---------------------------------

.. http:example:: http/complaints/award-complaint-submit.http
   :code:

Cancelling Tender Award Complaint
=================================

Cancelling draft complaint by Complainant
-----------------------------------------

.. http:example:: http/complaints/award-complaint-mistaken.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. http:example:: http/complaints/award-complaint-accepted-stopped.http
   :code:

Complaints in Defense open tender
=================================
Complaint periods creation in Defense open tender differs from other procurement methods.

In moment of award activation (status changes to `active`):

- Complaint period is created for this award
- Complaint periods are created/updated for awards with `unsuccessful` status (if lots - only for active lots)

Claims are denied in Defense open tender

List awards after auction
-----------------------------------------
We have tender on qualification stage with 3 bids and one pending award

.. http:example:: ../defense/http/new-complaints-list-award.http
   :code:

Disqualification of first bid award
-----------------------------------------
Tender owner patches first bid award from `pending` to `unsuccessful`.
No complaint period for the award was created.

.. http:example:: ../defense/http/new-complaints-patch-award-unsuccessful.http
   :code:

Activation of second bid award
-----------------------------------------
Tender owner patches second bid award from `pending` to `active`.
Complaint period for the second bid award was created.

.. http:example:: ../defense/http/new-complaints-patch-award-active.http
   :code:

Also Complaint period for the first (unsuccessful) bid award was created.

.. http:example:: ../defense/http/new-complaints-list-award-2.http
   :code:

Cancellation of second bid award
-----------------------------------------
Tender owner patches second bid award from `active` to `cancelled`.
Complaint period for the award remains unchanged.

.. http:example:: ../defense/http/new-complaints-patch-award-cancelled.http
   :code:

Disqualification of second bid award
-----------------------------------------
Tender owner patches second bid award from `pending` to `unsuccessful`.
No complaint period for the award was created.

.. http:example:: ../defense/http/new-complaints-patch-award-unsuccessful-2.http
   :code:

Activation of third bid award
-----------------------------------------
One day time delay left.
Tender owner patches third bid award from `pending` to `active`.
Complaint period for the third bid award was created.

.. http:example:: ../defense/http/new-complaints-patch-award-active-2.http
   :code:

Also complaint period for the first and second (unsuccessful) bid award was created/updated.

.. http:example:: ../defense/http/new-complaints-list-award-3.http
   :code: