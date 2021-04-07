.. _electroniccatalogue_tutorial:

Tutorial
========

Framework creation
------------------

Only markets with 5th accreditation level can create frameworks. `ProcuringEntity` can have only `central` kind.
Framework can be created only for cpb that have `active: true` status https://prozorroukr.github.io/standards/organizations/authorized_cpb.json

Let’s create a framework:

.. include:: tutorial/create-electroniccatalogue.http
   :code:

We have `201 Created` response code, `Location` header and body with extra properties.

Framework was created in `draft` status. In this status any field, except technical, can be changed using PATCH method.

.. include:: tutorial/patch-electroniccatalogue-draft.http
   :code:

Uploading documentation
-----------------------

Procuring entity can upload files into the created framework. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/upload-framework-document.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/framework-documents.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/upload-framework-document-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/upload-framework-document-3.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/get-framework-document-3.http
   :code:

Framework activation
--------------------

The second step is moving the framework to `active` status.

`qualificationPeriod.endDate` should be in between 30 and 1095 days from activation moment.

There should be at least 1 document in addition to sign document.

.. include:: tutorial/patch-electroniccatalogue-draft-to-active.http
   :code:

After framework activation frameworks periods was calculated:

`enquiryPeriod` - first 10 full working days after activation.

`period` - period when suppliers can add submissions (except `enquiryPeriod`).

`qualificationPeriod` - last 30 full calendar days of framework when suppliers cannot add submissions but still can be qualified based on previous submissions.

.. include:: tutorial/get-framework.http
   :code:

Let's check what framework registry contains:

.. include:: tutorial/framework-listing.http
   :code:

We do see the internal `id` of a framework and its `dateModified` datestamp.

Modifying framework
-------------------

In `active` status only some fields can be changed: `telephone`, `name`, `email` for `procuringEntity.contactPoint`, `endDate` for `qualificationPeriod`, `description` and `documents`.

If `qualificationPeriod.endDate` was changed all periods will be recalculated.

.. include:: tutorial/patch-electroniccatalogue-active.http
   :code:

Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: tutorial/framework-listing.http
   :code:

Registering submission
----------------------

After activating framework, users can register their submissions in period from `framework.enquiryPeriod.endDate` to `period.Date`:

.. include:: tutorial/register-submission.http
   :code:

We have `201 Created` response code, `Location` header and body with extra properties.


Uploading Submission documentation
----------------------------------

Documents can be uploaded/changed only for submission in `draft` status.

Documents operations is same like in framework:

.. include:: tutorial/upload-submission-document.http
   :code:

.. include:: tutorial/get-submission-documents.http
   :code:


Deleting submission
-------------------

Submission can be deleted only in `draft` status:

.. include:: tutorial/deleting-submission.http
   :code:


Updating Submission
-------------------

Submission can be changed only in `draft` status:

.. include:: tutorial/updating-submission.http
   :code:

Submission activation
---------------------

Submission can be activated before `period.endDate`

.. include:: tutorial/activating-submission.http
   :code:

After activating the submission, a qualification object is automatically created and submission `qualificationID` field is filled.

Let's check what submission registry contains:

.. include:: tutorial/submission-listing.http
   :code:

Let's check created qualification object:

.. include:: tutorial/get-qualification.http
   :code:

All operations with qualification object can do only `framework_owner`.


Uploading qualification documentation
-------------------------------------

Documents can be uploaded/changed only for qualification in `pending` status.

Documents operations is same like in framework:

.. include:: tutorial/upload-qualification-document.http
   :code:

.. include:: tutorial/get-qualification-documents.http
   :code:


Canceled qualification
----------------------

Qualification can be cancelled only in `pending` status.

.. include:: tutorial/unsuccessful-qualification.http
   :code:

After cancelling qualification, related submission changed status from `active` to `complete`.

Let's check what happen with submissions after cancelling qualification:

.. include:: tutorial/get-submissions-by-framework-id.http
   :code:

Approve qualification
------------------------

Qualification can be approved only in `pending` status.

.. include:: tutorial/activation-qualification.http
   :code:

After approving qualification, if it was first active qualification system create agreement with contract
otherwise system add contract to agreement.

Let's check current framework

.. include:: tutorial/get-framework-with-agreement.http
   :code:

You can see that `agreementID` appeared in current framework, so let's check that agreement:

.. include:: tutorial/get-agreement.http
   :code:

As you can see agreement now in `active` status, and already have contract, so we can see that agreement in agreement feed:

.. include:: tutorial/agreement-listing.http
   :code:


Let's check what qualification registry contains:

.. include:: tutorial/qualification-listing.http
   :code:

Let's check all qualifications for current framework:

.. include:: tutorial/get-qualifications-by-framework-id.http
   :code:


Framework completing
--------------------

Framework is completed automatically at `qualificationPeriod.endDate` moment.

PATCH with new `qualificationPeriod.endDate` allow to complete framework earlier than was planned, but not earlier than 30 full calendar days from change moment.