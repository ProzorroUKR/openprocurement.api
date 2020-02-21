

Claim/Complaint Retrieval
=========================

Tender Qualification Claim/Complaint Retrieval
----------------------------------------------

You can list all Tender Qualification Claims/Complaints:

.. include:: http/tutorial/qualification-complaints-list.http
   :code:

And check individual complaint:

.. include:: http/tutorial/qualification-complaint.http
   :code:

Claim Submission
================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Claim.

Tender Qualification Claim Submission (with documents)
------------------------------------------------------

At first create a claim. Send POST request with bidder's access token.

.. include:: http/tutorial/qualification-complaint-submission.http
   :code:

Then upload necessary documents:

.. include:: http/tutorial/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification claim:

.. include:: http/tutorial/qualification-complaint-claim.http
   :code:

Tender Qualification Claim Submission (without documents)
---------------------------------------------------------

You can submit claim that does not need additional documents:

.. include:: http/tutorial/qualification-complaint-submission-claim.http
   :code:


Complaint Submission
====================

If tender qualification is favoriting certain supplier, or in any other viable case, participants can submit Tender Qualification Complaint.

Tender Qualification Complaint Submission (with documents)
----------------------------------------------------------

At first create a complaint. Send POST request with bidder's access token.

.. include:: http/tutorial/qualification-complaint-submission.http
   :code:

Then upload necessary documents:
   
.. include:: http/tutorial/qualification-complaint-submission-upload.http
   :code:

Submit tender qualification complaint:
   
.. include:: http/tutorial/qualification-complaint-complaint.http
   :code:

Tender Qualification Complaint Submission (without documents)
-------------------------------------------------------------

You can submit complaint that does not need additional documents:

.. include:: http/tutorial/qualification-complaint-submission-complaint.http
   :code:

Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. include:: http/tutorial/qualification-complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: http/tutorial/qualification-complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. include:: http/tutorial/qualification-complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: http/tutorial/qualification-complaint-post-tender-owner.http
   :code:

Claim's Answer
==============

Answer to resolved claim
------------------------

.. include:: http/tutorial/qualification-complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. include:: http/tutorial/qualification-complaint-satisfy.http
   :code:


Unsatisfying resolution
-----------------------

.. include:: http/tutorial/qualification-complaint-unsatisfy.http
   :code:


Complaint Resolution
====================

Rejecting Tender Qualification Complaint
----------------------------------------

.. include:: http/tutorial/qualification-complaint-reject.http
   :code:


Accepting Tender Qualification Complaint
----------------------------------------

.. include:: http/tutorial/qualification-complaint-accept.http
   :code:


Submitting Tender Qualification Complaint Resolution
----------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: http/tutorial/qualification-complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: http/tutorial/qualification-complaint-resolve.http
   :code:

Or declines it:

.. include:: http/tutorial/qualification-complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. include:: http/tutorial/qualification-complaint-resolved.http
   :code:

Cancelling Tender Qualification Complaint
=========================================

Cancelling not accepted complaint
---------------------------------

.. include:: http/tutorial/qualification-complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: http/tutorial/qualification-complaint-accepted-stopping.http
   :code:

.. include:: http/tutorial/qualification-complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: http/tutorial/qualification-complaint-accepted-stopped.http
   :code:
