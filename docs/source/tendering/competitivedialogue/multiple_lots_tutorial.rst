.. _competitivedialogue_mulitlot_tutorial:

Multiple Lots Tutorial
======================


Creating tender
---------------

Let's create tender:

.. include:: multiple_lots_tutorial/tender-post-attempt-json-data.http
   :code:

Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified.  Note that tender is created with `active.tendering` status.

The peculiarity of the Open EU procedure is that ``procurementMethodType`` was changed from ``belowThreshold`` to ``aboveThresholdEU``.
Also there is no opportunity to set up ``enquiryPeriod``, it will be assigned automatically.

Tender can contain several different lots. We can add lot using the following way:

.. include:: multiple_lots_tutorial/tender-add-lot.http
   :code:

Also you will need to update data about item's related lots:

.. include:: multiple_lots_tutorial/tender-add-relatedLot-to-item.http
   :code:

View tender listing:

.. include:: multiple_lots_tutorial/tender-listing-no-auth.http
   :code:

or view tender:

.. include:: multiple_lots_tutorial/tender-view.http
   :code:



Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.

Bidder can register a bid for lot №1:

.. include:: multiple_lots_tutorial/bid-lot1.http
   :code:

Bidder can register bids for all lots:

.. include:: multiple_lots_tutorial/bid-lot2.http
   :code:

Then bidder should upload technical and private documents of proposal.

We can update tender during ``active.tendering`` period. Bids will be invalid after updating tender. For example, let's reduce the lot price to 400.

.. include:: multiple_lots_tutorial/tender-invalid-all-bids.http
   :code:

Here is the bidder's proposal after tender was updated.

.. include:: multiple_lots_tutorial/bid-lot1-invalid-view.http
   :code:

Firstly bidder has to renew bid, even if he was placing a bid just for a lot №1.

.. include:: multiple_lots_tutorial/bid-lot1-update-view.http
   :code:

Then bidder has to renew bid only for a lot №1.

.. include:: multiple_lots_tutorial/bid-lot2-update-view.http
   :code:


Bid Qualification
-----------------

CompetitiveDialogue procedure requires bid's value qualification.

Let's view tender: 

.. include:: multiple_lots_tutorial/tender-view-pre-qualification.http
   :code:

Let's list qualifications:

.. include:: multiple_lots_tutorial/qualifications-view.http
   :code:

Approve bid's value through qualification objects:

.. include:: multiple_lots_tutorial/tender-activate-qualifications.http
   :code:


Procuring entity approves qualifications by switching to next status:

.. include:: multiple_lots_tutorial/tender-view-pre-qualification-stand-still.http
   :code:

There is 10 day stand-still period set in `qualificationPeriod`.

Second stage
------------

On second stage we must register new bids, but register bid can only users who was approved on first stage

Let's try register bid by procuring which didn't was on first stage

.. include:: multiple_lots_tutorial/register_bad_bid.http
   :code:

We catch error.

Now procuring which was approved on 1 lot.

.. include:: multiple_lots_tutorial/register_ok_bid.http
   :code:

Successs!

And now try register on lot which he not allowed.

.. include:: multiple_lots_tutorial/register_bad_not_allowed_lot.http
   :code:

We again catch error. So we can conclude that, only user from first stage can register bid on second stage.
