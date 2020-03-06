

Claim/Complaint Retrieval
=========================

Tender Conditions Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Conditions Claims/Complaints:

.. include:: http/tutorial/complaints-list.http
   :code:

And check individual complaint or claim:

.. include:: http/tutorial/complaint.http
   :code:

Claim Submission
================

If tender conditions are favoriting particular supplier, or in any other viable case, any registered user can submit Tender Conditions Claim.

Tender Conditions Claim Submission (with documents)
---------------------------------------------------

At first create a claim:

.. include:: http/tutorial/claim-submission.http
   :code:

Then upload necessary documents:
   
.. include:: http/tutorial/complaint-submission-upload.http
   :code:

Submit tender conditions claim:
   
.. include:: http/tutorial/complaint-claim.http
   :code:

Tender Conditions Claim Submission (without documents)
------------------------------------------------------

You can submit claim that does not need additional documents:

.. include:: http/tutorial/complaint-submission-claim.http
   :code:

Complaint Submission
====================

Any registered user can submit Tender Conditions Complaint.


Tender Conditions Complaint Submission (with documents)
-------------------------------------------------------

At first create a draft:

.. include:: http/tutorial/complaint-submission.http
   :code:

Then upload necessary documents:
   
.. include:: http/tutorial/complaint-submission-upload.http
   :code:

Submit tender conditions complaint:
   
.. include:: http/tutorial/complaint-complaint.http
   :code:

Tender Conditions Complaint Submission (without documents)
----------------------------------------------------------

You can submit complaint that does not need additional documents:

.. include:: http/tutorial/complaint-submission-complaint.http
   :code:

Complaint Posts
===============

Once complaint is in `pending` or `accepted` status reviewer can submit a post to complaint.

Tender Conditions Complaint Posts (with complaint owner)
--------------------------------------------------------

Reviewer can submit a post to complaint owner:

.. include:: http/tutorial/complaint-post-reviewer-complaint-owner.http
   :code:

Complaint owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: http/tutorial/complaint-post-complaint-owner.http
   :code:

Tender Conditions Complaint Posts (with tender owner)
--------------------------------------------------------

Reviewer can submit a post to tender owner:

.. include:: http/tutorial/complaint-post-reviewer-tender-owner.http
   :code:

Tender owner can submit a reply post to reviewer by setting reviewer's post `id` as `relatedPost`:

.. include:: http/tutorial/complaint-post-tender-owner.http
   :code:


Claim's Answer
==============

Answer to resolved claim
------------------------

.. include:: http/tutorial/complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. include:: http/tutorial/complaint-satisfy.http
   :code:


Escalate claim to complaint
---------------------------

.. include:: http/tutorial/complaint-escalate.http
   :code:


Complaint Resolution
====================

Rejecting Tender Conditions Complaint
-------------------------------------

.. include:: http/tutorial/complaint-reject.http
   :code:


Accepting Tender Conditions Complaint
-------------------------------------

.. include:: http/tutorial/complaint-accept.http
   :code:


Submitting Tender Conditions Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: http/tutorial/complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: http/tutorial/complaint-resolve.http
   :code:

Or declines it:

.. include:: http/tutorial/complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. include:: http/tutorial/complaint-resolved.http
   :code:

Cancelling Tender Conditions Complaint
======================================

Cancelling not accepted complaint
---------------------------------

.. include:: http/tutorial/complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: http/tutorial/complaint-accepted-stopping.http
   :code:

.. include:: http/tutorial/complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: http/tutorial/complaint-accepted-stopped.http
   :code:
