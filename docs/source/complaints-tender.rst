.. Kicking page rebuild 2014-10-30 17:00:08

Claim/Complaint Retrieval
=========================

Tender Conditions Claim/Complaint Retrieval
-------------------------------------------

You can list all Tender Conditions Claims/Complaints:

.. include:: tutorial/complaints-list.http
   :code:

And check individual complaint or claim:

.. include:: tutorial/complaint.http
   :code:

Claim Submission
================

If tender conditions are favoriting particular supplier, or in any other viable case, any registered user can submit Tender Conditions Claim.

Tender Conditions Claim Submission (with documents)
---------------------------------------------------

At first create a claim:

.. include:: tutorial/complaint-submission.http
   :code:

Then upload necessary documents:
   
.. include:: tutorial/complaint-submission-upload.http
   :code:

Submit tender conditions claim:
   
.. include:: tutorial/complaint-claim.http
   :code:

Tender Conditions Claim Submission (without documents)
------------------------------------------------------

You can submit claim that does not need additional documents:

.. include:: tutorial/complaint-submission-claim.http
   :code:

Complaint Submission
====================

Any registered user can submit Tender Conditions Complaint.


Tender Conditions Complaint Submission (with documents)
-------------------------------------------------------

At first create a draft:

.. include:: tutorial/complaint-submission.http
   :code:

Then upload necessary documents:
   
.. include:: tutorial/complaint-submission-upload.http
   :code:

Submit tender conditions complaint:
   
.. include:: tutorial/complaint-complaint.http
   :code:

Tender Conditions Complaint Submission (without documents)
----------------------------------------------------------

You can submit complaint that does not need additional documents:

.. include:: tutorial/complaint-submission-complaint.http
   :code:


Claim's Answer
==============

Answer to resolved claim
------------------------

.. include:: tutorial/complaint-answer.http
   :code:


Satisfied Claim
===============

Satisfying resolution
---------------------

.. include:: tutorial/complaint-satisfy.http
   :code:


Escalate claim to complaint
---------------------------

.. include:: tutorial/complaint-escalate.http
   :code:


Complaint Resolution
====================

Rejecting Tender Conditions Complaint
-------------------------------------

.. include:: tutorial/complaint-reject.http
   :code:


Accepting Tender Conditions Complaint
-------------------------------------

.. include:: tutorial/complaint-accept.http
   :code:


Submitting Tender Conditions Complaint Resolution
-------------------------------------------------

The Complaint Review Body uploads the resolution document:

.. include:: tutorial/complaint-resolution-upload.http
   :code:

And either resolves complaint:

.. include:: tutorial/complaint-resolve.http
   :code:

Or declines it:

.. include:: tutorial/complaint-decline.http
   :code:

Submitting Resolution Confirmation
----------------------------------

.. include:: tutorial/complaint-resolved.http
   :code:

Cancelling Tender Conditions Complaint
======================================

Cancelling not accepted complaint
---------------------------------

.. include:: tutorial/complaint-cancel.http
   :code:

Cancelling accepted complaint by Complainant
--------------------------------------------

.. include:: tutorial/complaint-accepted-stopping.http
   :code:

.. include:: tutorial/complaint-stopping-stopped.http
   :code:

Cancelling accepted complaint by Reviewer
-----------------------------------------

.. include:: tutorial/complaint-accepted-stopped.http
   :code:
