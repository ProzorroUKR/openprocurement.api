.. _milestones:

Payment milestones
==================

Payment information can be specified via tender `milestones` list of :ref:`Milestone <milestone>` objects

.. include:: http/milestones/tender-post-milestones.http
   :code:


Let's update `milestones`:


.. include:: http/milestones/tender-patch-milestones.http
   :code:

For multi-lot tenders every :ref:`Milestone <milestone>` object can be connected to a specific lot


.. include:: http/milestones/tender-patch-lot-milestones.http
   :code:

Be careful, :ref:`lot <lot>` objects cannot be deleted while there are any connected milestones

.. include:: http/milestones/tender-delete-lot-milestones-error.http
   :code: