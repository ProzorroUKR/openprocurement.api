.. _tutorial:

Multiple Lots Tutorial
======================


Creating tender
---------------

Let's provide the data attribute in the submitted body :

.. include:: multiple_lots_tutorial/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified.  Note that tender is created with `active.tendering` status.

The peculiarity of the Open EU procedure is that ``procurementMethodType`` was changed from ``belowThreshold`` to ``aboveThresholdEU``.
Also there is no opportunity to set up ``enquiryPeriod``, it will be assigned automatically.

We can add lot

.. include:: multiple_lots_tutorial/tender-add-lot.http
   :code:

and update items related lots

.. include:: multiple_lots_tutorial/tender-add-relatedLot-to-item.http
   :code:

Tender listing

.. include:: multiple_lots_tutorial/tender-listing-no-auth.http
   :code:

View tender

.. include:: multiple_lots_tutorial/tender-view.http
   :code:



Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.

Bidder can register a bid for lot 1:

.. include:: multiple_lots_tutorial/bid-lot1.http
   :code:

Bidder can register a bid for all lots:

.. include:: multiple_lots_tutorial/bid-lot2.http
   :code:

Then bidder should upload proposal technical and private documents

We can update update tender in ``active.tendering`` period. Bids will be invalid after updating tender. Let the lot price reduced to 400.

.. include:: multiple_lots_tutorial/tender-invalid-all-bids.http
   :code:

Here is the bidder proposal after tender was updated.

.. include:: multiple_lots_tutorial/bid-lot1-invalid-view.http
   :code:

First bidder renewed bid, although he was bidding just a lot №1

.. include:: multiple_lots_tutorial/bid-lot1-update-view.http
   :code:

Then bidder renew bid only for lot №1

.. include:: multiple_lots_tutorial/bid-lot2-update-view.http
   :code:


Bid Qualification
-----------------

Open EU procedure requires bids value qualification.

Let's tender view: 

.. include:: multiple_lots_tutorial/tender-view-pre-qualification.http
   :code:
   
Approve bids value through qualification objects:

.. include:: multiple_lots_tutorial/tender-activate-qualifications.http
   :code:


Tender owner approves qualifications by switching to next status:

.. include:: multiple_lots_tutorial/tender-view-pre-qualification-stand-still.http
   :code:

You may notice 10 day stand-still time set in qualificationPeriod.   

   
