
.. _qualification_operations:

Qualification Operations
========================

When auction is over, the qualification process starts. The status of tender
is `active.qualification` then.  Right after results are submitted to
Central DB, there is award generated for auction winner.

Listing awards
~~~~~~~~~~~~~~

The pending award can be retrieved via request to list all available awards:

.. http:example:: http/qualification/awards-get.http
   :code:


When the award is in `pending` status, it means that procuring entity has
to review documents describing the bid and other bidder documents.

Disqualification
~~~~~~~~~~~~~~~~

The protocol of Qualification Committee decision should be uploaded as
document into award and later its status should switch to either `active`
(if it is accepted) or `unsuccessful` (if rejected).

.. note::
    Before making decision it is required to add sign document to award.

.. http:example:: http/qualification/award-pending-upload.http
   :code:

The Qualification Committee can upload several documents, for example, decisions to
prolong the qualification process - in order to allow the bidder to collect all
necessary documents or correct errors.  Such documents would help to have
procedure as transparent as possible and will reduce risk of cancellation by
Complaint Review Body.

.. http:example:: http/qualification/award-pending-unsuccessful.http
   :code:

Note that after award rejection the next bid in the value-sorted bid
sequence becomes subject of subsequent award.  For convenience you can use
the `Location` response header from the response above that is pointing
to an award in "pending" state.


Contract Awarding
~~~~~~~~~~~~~~~~~

Protocol upload:

.. sourcecode:: http

  POST /tenders/64e93250be76435397e8c992ed4214d1/awards/{}/documents HTTP/1.1

Confirming the Award:

.. sourcecode:: http

  PATCH /tenders/64e93250be76435397e8c992ed4214d1/awards/{} HTTP/1.1

  {
      "data":{
          "status": "active"
      }
  }

.. sourcecode:: http

  HTTP/1.1 200 OK

The procuring entity can wait until bidder provides all missing documents
(licenses, certificates, statements, etc.) or update original bid documents
to correct errors.  Alternatively, they can reject the bid if provided
documents do not satisfy the pass/fail criteria of tender (even before
full package of supplementary documents is available).

Cancelling Active Award
~~~~~~~~~~~~~~~~~~~~~~~

Sometimes Bidder refuses to sign the contract even after passing
qualification process.  In this case Procuring Entity is expected to be able
to reject approved award and disqualify Bid afterwards.

After we have Award with active status:

.. http:example:: http/qualification/award-active-get.http
   :code:

There is need to cancel it:

.. http:example:: http/qualification/award-active-cancel.http
   :code:

Note that there is Location header returned that aids in locating the "fresh"
award that is most likely subject for disqualification:

.. http:example:: http/qualification/award-active-cancel-upload.http
   :code:

.. http:example:: http/qualification/award-active-cancel-disqualify.http
   :code:

In the case when there is another Bid for qualification, there will be
Location header in the response pointing to its Award.


Cancellation of the decision on disqualification without the effect of a satisfied complaint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For some procedures, it is possible for the contracting authority to cancel its decision to reject a tenderer's offer when the award becomes unsuccessful,
only if there is no contract in the active status in the tender/lot.

The list of procedures:
 - competitiveOrdering
 - aboveThreshold
 - aboveThresholdUA
 - aboveThresholdEU
 - aboveThresholdUA.defense
 - simple.defense
 - competitiveDialogueUA.stage2
 - competitiveDialogueEU.stage2
 - esco

Unsuccessful award:

.. http:example:: http/qualification/awards-unsuccessful-get1.http
   :code:

Let's cancel unsuccessful award:

.. http:example:: http/qualification/awards-unsuccessful-cancel-wo-complaints.http
   :code:

The presence of a complaint in any status does not block this option.

No additional justification is provided for the cancellation of such a decision.

When the customer cancels the decision on award:unsuccessful, in this case, as with any cancellation of the decision, the award acquires the status `cancelled`, a new award `pending` is created, on which the customer must make a new decision:

.. http:example:: http/qualification/awards-unsuccessful-cancelled-get.http
   :code:

In this case, the existing `award:pending` and `award:active` automatically acquire the status `cancelled`.

Influence of Complaint Satisfaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If decision of the procuring entity is unfair any bidder can file
complaint and after proper review the whole awarding process can start from
the award in question.

Disqualification decision of procuring entity's qualification committee can be cancelled in the following cases:

* claim for this disqualification has been submitted (claim status is ``claim``);
* claim has been answered (claim status is ``answered``);
* complaint is pending review (complaint status is ``pending``);
* complaint has been satisfied by the Complaint Review Body (complaint status is ``resolved``).

After the disqualification decision cancellation it receives ``cancelled`` status. New pending award is generated and procuring entity is obliged to qualify it again (taking into consideration recommendations from the report of Complaint Review Body if there is one).

.. http:example:: http/qualification/awards-unsuccessful-get2.http
   :code:

.. http:example:: http/qualification/awards-unsuccessful-cancel.http
   :code:

.. http:example:: http/qualification/awards-unsuccessful-get3.http
   :code:
