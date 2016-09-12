.. _mulitlot_tutorial:

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


Awarding
--------

Addition of supplier information is the same for all procedures.

Add award for lot №1:

.. include:: multiple_lots_tutorial/tender-award.http
   :code:

Award confirmation:

.. include:: multiple_lots_tutorial/tender-award-approve.http
   :code:

The difference between ``startDate`` and ``endDate`` in ``complaintPeriod`` record for **negotiation** is 10 days and for **negotiation.quick** is 5 days.


Setting  contract value
-----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value.

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. include:: multiple_lots_tutorial/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.


Contract registration
---------------------

**Negotiation** and **Negotiation.quick** tender contract can be registered only after the stand-still (10 and 5 days period after the award confirmation).

.. include:: multiple_lots_tutorial/tender-contract-sign.http
   :code:
