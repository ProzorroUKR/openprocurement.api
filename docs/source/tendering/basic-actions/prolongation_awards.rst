.. _prolongation-awards:

Awards prolongation
====================

For all procedures, except :ref:`limited` and :ref:`belowThreshold`, there is an option to extend award period.

During award creation, field `period` appeared in every award. By default there are 5 working days for making decision:

.. http:example:: ./http/prolongation-awards/award-get.http
   :code:

To extend this period to 20 days, the procuring entity should add milestone with code `extensionPeriod`:

.. http:example:: ./http/prolongation-awards/award-milestone-extension-post.http
   :code:

After that it is required to add document with `documentType: extensionReport`:

.. http:example:: ./http/prolongation-awards/award-extension-report-post.http
   :code:

Only one document with type `extensionReport` could be in award:

.. http:example:: ./http/prolongation-awards/award-extension-report-invalid-post.http
   :code:

Now look at award, we will see that field `period.endDate` has been changed from 5 working days to 20 working days from award creation date:

.. http:example:: ./http/prolongation-awards/award-extension-get.http
   :code:
