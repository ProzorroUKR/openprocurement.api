

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

Tender Award Complaint Submission (with documents)
---------------------------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. http:example:: http/complaints/award-complaint-submission.http
   :code:

Then upload necessary documents:
   
.. http:example:: http/complaints/award-complaint-submission-upload.http
   :code:

Submit tender award complaint:
   
.. http:example:: http/complaints/award-complaint-complaint.http
   :code:

Tender Award Complaint Submission (without documents)
-----------------------------------------------------

You can submit complaint that does not need additional documents:

.. http:example:: http-outdated/complaints/award-complaint-submission-complaint.http
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

Cancelling not accepted(pending) complaint by Reviewer
------------------------------------------------------

.. http:example:: http-outdated/complaints/award-complaint-mistaken.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. http:example:: http-outdated/complaints/award-complaint-accepted-stopping.http
   :code:

.. http:example:: http-outdated/complaints/award-complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. http:example:: http/complaints/award-complaint-accepted-stopped.http
   :code:
