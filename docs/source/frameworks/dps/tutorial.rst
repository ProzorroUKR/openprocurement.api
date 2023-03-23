.. _framework_dps_tutorial:

Tutorial
========

Framework creation
------------------

Let’s create a framework:

.. http:example:: tutorial/create-framework.http
   :code:

We have `201 Created` response code, `Location` header and body with extra properties.

Framework was created in `draft` status. In this status any field, except technical, can be changed using PATCH method.

.. http:example:: tutorial/patch-framework-draft.http
   :code:

Uploading documentation
-----------------------

Procuring entity can upload files into the created framework. Uploading should
follow the :ref:`upload` rules.

.. http:example:: tutorial/upload-framework-document.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: tutorial/framework-documents.http
   :code:

And again we can confirm that there are two documents uploaded.

.. http:example:: tutorial/upload-framework-document-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. http:example:: tutorial/upload-framework-document-3.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: tutorial/get-framework-document-3.http
   :code:

Framework activation
--------------------

The second step is moving the framework to `active` status.

`qualificationPeriod.endDate` should be in between 30 and 1095 days from activation moment.

There should be at least 1 document in addition to sign document.

.. http:example:: tutorial/patch-framework-draft-to-active.http
   :code:

After framework activation frameworks periods was calculated:

`enquiryPeriod` - first 10 full working days after activation.

`period` - period when suppliers can add submissions (except `enquiryPeriod`).

`qualificationPeriod` - last 30 full calendar days of framework when suppliers cannot add submissions but still can be qualified based on previous submissions.

.. http:example:: tutorial/get-framework.http
   :code:

Let's check what framework registry contains:

.. http:example:: tutorial/framework-listing.http
   :code:

We do see the internal `id` of a framework and its `dateModified` datestamp.

Modifying framework
-------------------

In `active` status only some fields can be changed: `telephone`, `name`, `email` for `procuringEntity.contactPoint`, `endDate` for `qualificationPeriod`, `description` and `documents`.

If `qualificationPeriod.endDate` was changed all periods will be recalculated.

.. http:example:: tutorial/patch-framework-active.http
   :code:

Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: tutorial/framework-listing.http
   :code:

Registering submission
----------------------

After activating framework, users can register their submissions in period from `framework.enquiryPeriod.endDate` to `period.Date`:

.. http:example:: tutorial/register-submission.http
   :code:

We have `201 Created` response code, `Location` header and body with extra properties.


Uploading Submission documentation
----------------------------------

Documents can be uploaded/changed only for submission in `draft` status.

Documents operations is same like in framework:

.. http:example:: tutorial/upload-submission-document.http
   :code:

.. http:example:: tutorial/get-submission-documents.http
   :code:


Deleting submission
-------------------

Submission can be deleted only in `draft` status:

.. http:example:: tutorial/deleting-submission.http
   :code:


Updating Submission
-------------------

Submission can be changed only in `draft` status:

.. http:example:: tutorial/updating-submission.http
   :code:

Submission activation
---------------------

Submission can be activated before `period.endDate`

.. http:example:: tutorial/activating-submission.http
   :code:

After activating the submission, a qualification object is automatically created and submission `qualificationID` field is filled.

Let's check what submission registry contains:

.. http:example:: tutorial/submission-listing.http
   :code:

Let's check created qualification object:

.. http:example:: tutorial/get-qualification.http
   :code:

All operations with qualification object can do only `framework_owner`.


Uploading qualification documentation
-------------------------------------

Documents can be uploaded/changed only for qualification in `pending` status.

Documents operations is same like in framework:

.. http:example:: tutorial/upload-qualification-document.http
   :code:

.. http:example:: tutorial/get-qualification-documents.http
   :code:


Canceled qualification
----------------------

Qualification can be cancelled only in `pending` status.

.. http:example:: tutorial/unsuccessful-qualification.http
   :code:

After cancelling qualification, related submission changed status from `active` to `complete`.

Let's check what happen with submissions after cancelling qualification:

.. http:example:: tutorial/get-submissions-by-framework-id.http
   :code:

Approve qualification
------------------------

Qualification can be approved only in `pending` status.

.. http:example:: tutorial/activation-qualification.http
   :code:

After approving qualification, if it was first active qualification system create agreement with contract
otherwise system add contract to agreement.

Let's check current framework

.. http:example:: tutorial/get-framework-with-agreement.http
   :code:

You can see that `agreementID` appeared in current framework, so let's check that agreement:

.. http:example:: tutorial/get-agreement.http
   :code:

As you can see agreement now in `active` status, and already have contract, so we can see that agreement in agreement feed:

.. http:example:: tutorial/agreement-listing.http
   :code:


Let's check what qualification registry contains:

.. http:example:: tutorial/qualification-listing.http
   :code:

Let's check all qualifications for current framework:

.. http:example:: tutorial/get-qualifications-by-framework-id.http
   :code:


Framework completing
--------------------

Framework is completed automatically at `qualificationPeriod.endDate` moment.

PATCH with new `qualificationPeriod.endDate` allow to complete framework earlier than was planned, but not earlier than 30 full calendar days from change moment.