.. _electroniccatalogue_tutorial:

Tutorial
========

Framework creation and activation
---------------------------------

Only markets with 5th accreditation level can create frameworks.
Framework can be created only for cpb that have `active: true` status https://prozorroukr.github.io/standards/organizations/authorized_cpb.json

Let’s create a framework:

.. include:: tutorial/create-electroniccatalogue.http
   :code:

We have `201 Created` response code, `Location` header and body with extra properties.

Framework was created in `draft` status. In this status any field, except technical, can be changed using PATCH method.

.. include:: tutorial/patch-electroniccatalogue-draft.http
   :code:

The second step is moving the framework to `active` status.

`qualificationPeriod.endDate` should be in between 30 and 1095 days from activation moment.

There should be at least 1 document in addition to sign document.

.. include:: tutorial/patch-electroniccatalogue-draft-to-active.http
   :code:

After framework activation frameworks periods was calculated:

`enquiryPeriod` - first 10 full working days after activation when suppliers can ask questions and cannot add submissions to framework.

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

In `active` status only some fields can be changed.

If `qualificationPeriod.endDate` was changed all periods will be recalculated.

.. include:: tutorial/patch-electroniccatalogue-active.http
   :code:

Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: tutorial/framework-listing.http
   :code:

Framework completing
--------------------

Framework is completed automatically at `qualificationPeriod.endDate` moment.

PATCH with new `qualificationPeriod.endDate` allow to complete framework earlier than was planned, but not earlier than 30 full calendar days from change moment.