
.. _complaint-payments:


Complaints Payments
===================


Let's create a complaint:

.. include:: ./http/complaints-value/complaint-creation.http
   :code:


You can see `value` field that contains amount to be paid for this complaint


If currency of a tender is different from UAH,
posting complaint will request bank.gov.ua
and return complaint `value` in UAH anyway.
This also can cause connection errors of different types:

.. include:: ./http/complaints-value/complaint-creation-decoding.http
   :code:

.. include:: ./http/complaints-value/complaint-creation-connection.http
   :code:

In case of 409 code, request should be repeated. And it shouldn't in case of 422:

.. include:: ./http/complaints-value/complaint-creation-rur.http
   :code:

