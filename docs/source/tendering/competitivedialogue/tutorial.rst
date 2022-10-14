.. _competitivedialogue_tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/tenders` endpoint:

.. http:example:: tutorial/tender-listing.http
   :code:

Just invoking it reveals empty set.

Now let's attempt creating some tender:

.. http:example:: tutorial/tender-post-attempt.http
   :code:

Error states that the only accepted Content-Type is `application/json`.

Let's satisfy the Content-type requirement:

.. http:example:: tutorial/tender-post-attempt-json.http
   :code:

Error states that no `data` has been found in JSON body.


.. index:: Tender

Creating tender on first stage
------------------------------

Let's provide the data attribute in the submitted body :

.. http:example:: tutorial/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified.  Note that tender is created with `draft` status.

The peculiarity of the CompetitiveDialogue procedure is that ``procurementMethodType`` can be ``CompetitiveDialogueEU`` or ``CompetitiveDialogueUA``.

If you choice ``CompetitiveDialogueEU`` on second stage will be created procedure which similar on  Open EU, if
``CompetitiveDialogueUA`` then on Open UA.

Also there is no opportunity to set up ``enquiryPeriod``, it will be assigned automatically.

Let's access the URL of the created object (the `Location` header of the response):

.. http:example:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

Let's see what listing of tenders reveals us:

.. http:example:: tutorial/tender-listing-no-auth.http
   :code:

We don't see internal `id` of tender, because tender appears in the listing from `active.tendering` status.

Tender activating
-----------------

At first we needed to add EXCLUSION criteria to our tender(:ref:`About criteria you can read here<criteria_operation>`).

.. http:example:: tutorial/add-exclusion-criteria.http
   :code:

After adding needed criteria we can activate our tender, so let's do that:

.. http:example:: tutorial/tender-activating.http
   :code:

Let's see what listing of tenders reveals us:

.. http:example:: tutorial/active-tender-listing-no-auth.http
   :code:

Now We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.


Modifying tender
----------------

Let's update tender by supplementing it with all other essential properties:

.. http:example:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: tutorial/tender-listing-after-patch.http
   :code:

Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. http:example:: tutorial/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. http:example:: tutorial/update-tender-after-enqiery-with-update-periods.http
   :code:

Procuring entity can set bid guarantee:

.. http:example:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. http:example:: tutorial/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: tutorial/tender-documents.http
   :code:


And again we can confirm that there are two documents uploaded.

.. http:example:: tutorial/tender-documents-2.http
   :code:


And we can see that it is overriding the original version:

.. http:example:: tutorial/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions:

.. http:example:: tutorial/ask-question.http
   :code:

Procuring entity can answer them:

.. http:example:: tutorial/answer-question.http
   :code:

One can retrieve either questions list:

.. http:example:: tutorial/list-question.http
   :code:

or individual answer:

.. http:example:: tutorial/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. http:example:: tutorial/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.

Bidder can register a bid with `draft` status:

.. http:example:: tutorial/register-bidder.http
   :code:

And append responses for criteria requirements:

.. http:example:: tutorial/add-requirement-responses-to-bidder.http
   :code:

and approve to pending status:

.. http:example:: tutorial/activate-bidder.http
   :code:

Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal technical document(s):

.. http:example:: tutorial/upload-bid-proposal.http
   :code:


Document can be type descriptive decision.
If you want that document be descriptive decision need set `isDescriptionDecision`

First upload file

.. http:example:: tutorial/upload-bid-descriptive-decision-proposal.http
   :code:

Then set `isDescriptionDecision`

.. http:example:: tutorial/mark-bid-doc-decision-proposal.http
   :code:

Confidentiality
^^^^^^^^^^^^^^^

Documents can be either public or private:

  1. Privacy settings can be changed only for the latest version of the document.
  2. When you upload new version of the document, privacy settings are copied from the previous version.
  3. Privacy settings can be changed only during `tenderPeriod` (with `active.tendering` status).
  4. If tender has status `active.qualification` winner can upload only public documents.

Let's upload private document:

.. http:example:: tutorial/upload-bid-private-proposal.http
   :code:

To define the document as "private" - `confidentiality` and `confidentialityRationale` fields should be set.

`confidentiality` field value can be either `buyerOnly` (document is private) or `public` (document is publicly accessible).

Content of private documents (`buyerOnly`) can be accessed only by procuring entity or by participant who uploaded them.

`confidentialityRationale` field is required only for private documents and should contain at least 30 characters.

Let's mark the document as "private":

.. http:example:: tutorial/mark-bid-doc-private.http
   :code:

When documents with parameter ``isDescriptionDecision`` set to privacy ``confidentialityRationale`` must be missed.

Let's mark the document as "private":

.. http:example:: tutorial/mark-bid-doc-decision-private.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: tutorial/bidder-documents.http
   :code:

.. _competitivedialogue_envelopes:


Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. http:example:: tutorial/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. http:example:: tutorial/bidder-activate-after-changing-tender.http
   :code:

Competitive Dialogue procedure demands at least three bidders:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:

Register two more bid:

.. http:example:: tutorial/register-3rd-bidder.http
   :code:

Batch-mode bid registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register one more bid with documents using single request (batch-mode):

.. http:example:: tutorial/register-4rd-bidder.http
   :code:


.. index:: Qualification

Bid Qualification
-----------------

Competitive Dialogue procedure requires bid qualification.

Let's list qualifications:


.. http:example:: tutorial/qualifications-listing.http
   :code:

Approve first three bids through qualification objects:

.. http:example:: tutorial/approve-qualification1.http
   :code:

.. http:example:: tutorial/approve-qualification2.http
   :code:

.. http:example:: tutorial/approve-qualification4.http
   :code:

We can also reject bid:

.. http:example:: tutorial/reject-qualification3.http
   :code:

And check that qualified bids are switched to `active`:

.. http:example:: tutorial/qualificated-bids-view.http
   :code:

Rejected bid is not shown in `bids/` listing.

We can access rejected bid by id:

.. http:example:: tutorial/rejected-bid-view.http
   :code:

Procuring entity approves qualifications by switching to next status:

.. http:example:: tutorial/pre-qualification-confirmation.http
   :code:

You may notice 10 day stand-still time set in `qualificationPeriod`.


Ready to stage2
---------------

When qualification period end tender will has status active.stage2.pending

Lets look on your tender

.. http:example:: tutorial/stage2-pending.http
   :code:


Hoт purchasing can set that he is ready for second stage, by setting status to ``active.stage2.waiting``.

.. http:example:: tutorial/stage2-waiting.http
   :code:


Get token for second stage
--------------------------

When tender status is ``complete``, we can get id new stage.

First lets look on tender and find field ``stage2TenderID``

.. http:example:: tutorial/tender_stage1_complete.http
   :code:


Form making changes in second stage we need token

.. http:example:: tutorial/tender_stage2_get_token.http
    :code:

Make changes second stage
-------------------------

Good, now we get token, and can make changes, so lets change status from ``draft.stage2`` to ``active.tendering``


.. http:example:: tutorial/tender_stage2_modify_status.http
    :code:

Stage2 EU
---------

.. toctree::
    :maxdepth: 1

    tutorial_stage2EU

Stage2 UA
---------

.. toctree::
    :maxdepth: 1

    tutorial_stage2UA
