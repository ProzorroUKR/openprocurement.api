.. _tutorial:

Tutorial
========

Plan creation
---------------

Creating plan procurement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s create a plan:

.. include:: tutorial/create-plan.http
   :code:

We have `201 Created` response code, `Location` header and body with extra `id`, `planID`, and `dateModified` properties.

Let's check what plan registry contains:

.. include:: tutorial/plan-listing.http
   :code:

We do see the internal `id` of a plan (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/plans/`) and its `dateModified` datestamp.


Modifying plan
~~~~~~~~~~~~~~~~

Let's update plan by supplementing it with all other essential properties:

.. include:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing plan data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: tutorial/plan-listing-after-patch.http
   :code:
