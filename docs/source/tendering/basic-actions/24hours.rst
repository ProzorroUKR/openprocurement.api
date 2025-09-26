.. _24hours:

"24 hours"
==========

During the qualification process (or pre-qualification if the procedure has one)
procuring entity can decide to allow a bidder to upload more documents to their bid, add/change `evidences` for requirementResponses. or update particular fields in bid.

The fields that may be updated during 24 hours milestone:

* requirementResponses
* items.unit.value.amount
* subcontractingDetails
* tenderers.signerInfo


Example of posting :ref:`qualificationmilestone` for qualification

.. http:example:: ./http/24hours/award-milestone-post.http
   :code:


Example of pre-qualification


.. http:example:: ./http/24hours/qualification-milestone-post.http
   :code:

After adding milestone `24h`, the award/qualification should be signed with `documentType: deviationReport`.

Signing :ref:`qualificationmilestone` for qualification:

.. http:example:: ./http/24hours/award-sign-milestone-24.http
   :code:

Signing milestone of pre-qualification:

.. http:example:: ./http/24hours/qualification-sign-milestone-24.http
   :code:

Only one document with type `deviationReport` could be in award/qualification:

.. http:example:: ./http/24hours/award-sign-milestone-24-duplicate.http
   :code:

The "dueDate" field in the response indicates the end of the period when
procuring entity is unable to make a decision on the qualification object


.. http:example:: ./http/24hours/award-patch.http
   :code:


The bidder can post new documents to their bid


.. http:example:: ./http/24hours/post-doc.http
   :code:


The bidder can update their documents

.. http:example:: ./http/24hours/put-doc.http
   :code:


The bidder can update some fields in bid:

.. http:example:: ./http/24hours/patch-bid.http
   :code:

If updated field is not forbidden, we will see an error:

.. http:example:: ./http/24hours/patch-bid-invalid.http
   :code:

The bidder can update `requirementResponses` for his bid.

For example, the bidder can delete `requirementResponses` from one requirementGroup in article 17:

.. http:example:: ./http/24hours/delete-article-17-req-response.http
   :code:

and then add new `requirementResponses` for another requirementGroup in article 17:

.. http:example:: ./http/24hours/add-article-17-req-response.http
   :code:

The bidder can add/change `evidences` for requirementResponses:

.. http:example:: ./http/24hours/add-req-responses-evidences.http
   :code:

If milestone `dueDate` already passed, it is forbidden to patch any field in bid:

.. http:example:: ./http/24hours/patch-bid-forbidden.http
   :code:
