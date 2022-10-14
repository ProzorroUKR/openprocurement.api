

Claim/Complaint Retrieval
=========================

Tender Award Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Award Claims/Complaints:

.. include:: http/complaints/award-complaints-list.http
   :code:

And check individual complaint:

.. include:: http/complaints/award-complaint.http
   :code:

Complaint Submission
====================

If tender award is favoriting certain supplier, or in any other viable case, participants who were admitted to auction can submit Tender Award Complaint.

Tender Award Complaint Submission
---------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. include:: http/complaints/award-complaint-submission.http
   :code:

This step is optional. Upload documents:

.. include:: http/complaints/award-complaint-submission-upload.http
   :code:

Submit tender award complaint:

.. include:: http/complaints/award-complaint-complaint.http
   :code:


Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. include:: http/complaints/award-complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: http/complaints/award-complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. include:: http/complaints/award-complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: http/complaints/award-complaint-post-tender-owner.http
   :code:

Complaint Resolution
====================

Rejecting Tender Award Complaint
-------------------------------------

.. include:: http/complaints/award-complaint-reject.http
   :code:


Accepting Tender Award Complaint
-------------------------------------

.. include:: http/complaints/award-complaint-accept.http
   :code:


Submitting Tender Award Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: http/complaints/award-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: http/complaints/award-complaint-resolve.http
   :code:

Or declines it:

.. include:: http/complaints/award-complaint-decline.http
   :code:

Correcting problems
-------------------

If tender award complaint was satisfied by the Complaint Review Body, then procuring entity has to correct problems.

One of the possible solutions is award cancellation:


.. include:: http/complaints/award-complaint-satisfied-resolving.http
   :code:

After award cancellation system generates new award. Its location is present in the `Location` header of response.

Submitting Resolution Confirmation
----------------------------------
When complaint has been successfully resolved, procuring entity submits resolution confirmation.

.. include:: http/complaints/award-complaint-resolved.http
   :code:

Submitting complaint to new award
---------------------------------

.. include:: http/complaints/award-complaint-submit.http
   :code:

Cancelling Tender Award Complaint
=================================

Cancelling draft complaint by Complainant
-----------------------------------------

.. include:: http/complaints/award-complaint-mistaken-2020-04-19.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: http-outdated/complaints/award-complaint-accepted-stopping.http
   :code:

.. include:: http-outdated/complaints/award-complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: http/complaints/award-complaint-accepted-stopped.http
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

.. include:: ../defense/http/new-complaints-list-award.http
   :code:

Disqualification of first bid award
-----------------------------------------
Tender owner patches first bid award from `pending` to `unsuccessful`.
No complaint period for the award was created.

.. include:: ../defense/http/new-complaints-patch-award-unsuccessful.http
   :code:

Activation of second bid award
-----------------------------------------
Tender owner patches second bid award from `pending` to `active`.
Complaint period for the second bid award was created.

.. include:: ../defense/http/new-complaints-patch-award-active.http
   :code:

Also Complaint period for the first (unsuccessful) bid award was created.

.. include:: ../defense/http/new-complaints-list-award-2.http
   :code:

Cancellation of second bid award
-----------------------------------------
Tender owner patches second bid award from `active` to `cancelled`.
Complaint period for the award remains unchanged.

.. include:: ../defense/http/new-complaints-patch-award-cancelled.http
   :code:

Disqualification of second bid award
-----------------------------------------
Tender owner patches second bid award from `pending` to `unsuccessful`.
No complaint period for the award was created.

.. include:: ../defense/http/new-complaints-patch-award-unsuccessful-2.http
   :code:

Activation of third bid award
-----------------------------------------
One day time delay left.
Tender owner patches third bid award from `pending` to `active`.
Complaint period for the third bid award was created.

.. include:: ../defense/http/new-complaints-patch-award-active-2.http
   :code:

Also complaint period for the first and second (unsuccessful) bid award was created/updated.

.. include:: ../defense/http/new-complaints-list-award-3.http
   :code: