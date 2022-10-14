.. _milestones:

Payment milestones
==================

Payment information can be specified via tender `milestones` list of :ref:`Milestone <milestone>` objects

.. http:example:: http/milestones/tender-post-milestones.http
   :code:


Let's update `milestones`:


.. http:example:: http/milestones/tender-patch-milestones.http
   :code:

For multi-lot tenders every :ref:`Milestone <milestone>` object can be connected to a specific lot


.. http:example:: http/milestones/tender-patch-lot-milestones.http
   :code:

Be careful, :ref:`lot <lot>` objects cannot be deleted while there are any connected milestones

.. http:example:: http/milestones/tender-delete-lot-milestones-error.http
   :code: