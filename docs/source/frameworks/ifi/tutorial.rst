.. _framework_ifi_tutorial:

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

`qualificationPeriod.endDate` should be in between 365 and 1461 days from activation moment.

There should be at least 1 document in addition to sign document.

.. http:example:: tutorial/patch-framework-draft-to-active.http
   :code:

After framework activation frameworks periods was calculated:

`enquiryPeriod` - first 10 full working days after activation.

`period` - period when suppliers can add submissions.

`qualificationPeriod` - last 30 full calendar days of framework when suppliers cannot add submissions but still can be qualified based on previous submissions.

.. http:example:: tutorial/get-framework.http
   :code:

Let's check what framework registry contains:

.. http:example:: tutorial/framework-listing.http
   :code:

We do see the internal `id` of a framework and its `dateModified` datestamp.

Modifying framework
-------------------

In `active` status only some fields can be changed: `telephone`, `name`, `email` for `procuringEntity.contactPoint`, `description` and `documents`.

.. http:example:: tutorial/patch-framework-active.http
   :code:

Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: tutorial/framework-listing.http
   :code:

Modifying qualificationPeriod in active framework
--------------------------------------------------

Also in `active` status can be changed `endDate` for `qualificationPeriod` but it can be done only using another endpoint.

There are validations for changing `qualificationPeriod.endDate`:

* qualificationPeriod.endDate couldn't be less than 30 full calendar days from now
* qualificationPeriod.endDate couldn't be more than 1461 full calendar days from now

It is allowed to modify `qualificationPeriod` only by framework owner using `changes`.

Fields for modifying period:

* `qualificationPeriod.endDate` (in `change.modifications`)
* `rationale`
* `rationaleType`
* `documents` (optional)

Let's try to change `qualificationPeriod.endDate` with soon date:

.. http:example:: tutorial/patch-framework-active-qualification-period-too-soon.http
   :code:

Let's try to prolong `qualificationPeriod.endDate` with late date:

.. http:example:: tutorial/patch-framework-active-qualification-period-too-late.http
   :code:

Success changing of `qualificationPeriod`:

.. http:example:: tutorial/patch-framework-active-qualification-period.http
   :code:

There is special parameter `opt_context` for getting change data for signing:

.. http:example:: tutorial/get-change-sign-data.http
   :code:

For more detail about signing the data with context: :ref:`sign-data`.

Then the signature should be added to change:

.. http:example:: tutorial/sign-framework-active-qualification-period.http
   :code:

If `qualificationPeriod.endDate` was changed all periods will be recalculated.

Let's look at framework:

.. http:example:: tutorial/get-framework-after-qualification-period-modified.http
   :code:

There is a new object `changes` in framework with previous `qualificationPeriod.endDate` and new one. All period changes will be saved in this object.

Registering submission
----------------------

After activating framework, users can register their submissions in period from `framework.period.startDate` to `framework.period.endDate`:

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

Confidential documents for submissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documents can be public or confident.

Confidentiality may be applied/changed only for submission in `draft` status.
It is required to add `confidentialityRationale` with `confidentiality: buyerOnly`.

Let's add documents with `confidentiality` as `buyerOnly` and look what we've got:

.. http:example:: tutorial/upload-submission-conf-docs-wo-rationale.http
   :code:

Let's add `confidentialityRationale`:

.. http:example:: tutorial/upload-submission-conf-docs.http
   :code:

The bidder and framework owner see these kind of documents and can download:

.. http:example:: tutorial/get-submission-conf-docs-by-owner.http
   :code:

All others can't read the document:

.. http:example:: tutorial/get-submission-conf-docs-by-public.http
   :code:

Nobody but the owner of submission and framework can download the confidential document:

.. http:example:: tutorial/upload-submission-conf-doc-by-public.http
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

Before cancelling qualification it is required to add sign document to qualification. If there is no sign document during cancelling, we will see an error:

.. http:example:: tutorial/evaluation-reports-document-required-for-cancelling.http
   :code:

Sign document should have `documentType: evaluationReports` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/add-evaluation-reports-document-for-cancelling.http
   :code:

Then it is allowed to cancel qualification:

.. http:example:: tutorial/unsuccessful-qualification.http
   :code:

After cancelling qualification, related submission changed status from `active` to `complete`.

Let's check what happen with submissions after cancelling qualification:

.. http:example:: tutorial/get-submissions-by-framework-id.http
   :code:

Approve qualification
------------------------

Qualification can be approved only in `pending` status.

Before activating qualification it is required to add sign document to qualification. If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/evaluation-reports-document-required.http
   :code:

Sign document should have `documentType: evaluationReports` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/add-evaluation-reports-document.http
   :code:

Then it is allowed to activate qualification:

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