.. _24hours:

"24 hours"
==========

During the qualification process (or pre-qualification if the procedure has one)
procuring entity can decide to allow a bidder to upload more documents to their bid


Example of posting :ref:`qualificationmilestone` for qualification

.. include:: ./http/24hours/award-milestone-post.http
   :code:


Example of pre-qualification


.. include:: ./http/24hours/qualification-milestone-post.http
   :code:


The "dueDate" field in the response indicates the end of the period when
procuring entity is unable to make a decision on the qualification object


.. include:: ./http/24hours/award-patch.http
   :code:


The bidder can post new documents to their bid


.. include:: ./http/24hours/post-doc.http
   :code:


The bidder can update their documents

.. include:: ./http/24hours/put-doc.http
   :code:
