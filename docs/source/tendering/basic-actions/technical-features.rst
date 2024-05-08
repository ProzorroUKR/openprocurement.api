.. _technical_features:


Technical Features
==================


Procedures with technical features
----------------------------------

Technical features available in these procedures:
 - aboveThresholdUA
 - aboveThresholdEU
 - belowThreshold
 - competitiveDialogueUA
 - competitiveDialogueEU
 - competitiveDialogueUA.stage2
 - competitiveDialogueEU.stage2
 - competitiveOrdering
 - closeFrameworkAgreementUA
 - esco
 - priceQuotation


Creating tender for technical features
--------------------------------------

You can set id of catalogue object in field `profile` or `category` to item.
If you try set `profile` and `category` together to item, you will get an error:

.. http:example:: http/techfeatures/disallowed-profile-category-together.http
   :code:

if such profile or category doesn't exist in catalogue service, ypu will get an error:

.. http:example:: http/techfeatures/item-profile-not-found.http
   :code:


Also catalogue item should be in `active` status:

.. http:example:: http/techfeatures/item-profile-not-active.http
   :code:


So if you set `id` of correct profile/category, you can create tender:

.. http:example:: http/techfeatures/tender-with-item-profile-created.http
   :code:


Create technical feature criteria
---------------------------------

If you want create technical feature criteria, you should set `CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES`
to `criterion.classification.id` and `relatedItem` to item with relates to profile/category .

If you try to create technical feature criteria without relatesTo to item, you'll get error:

.. http:example:: http/techfeatures/create-tech-criteria-without-related-item.http
   :code:


Also if you try to create criteria with relatedItem without profile/category you'll get error:

.. http:example:: http/techfeatures/create-tech-criteria-for-items-without-profile.http
   :code:


So if all rules are met, you can create technical feature criteria:

.. http:example:: http/techfeatures/tender-with-item-profile-created.http
   :code: