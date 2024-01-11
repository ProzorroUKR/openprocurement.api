restrictedDerivatives
=====================

Create Framework with restricted access
---------------------------------------

First create framework with restricted access by `Broker`.
To do this, we need to set ``restricted_derivatives`` field to ``true`` in ``config`` section of framework creation request.

.. http:example:: http/restricted/framework-create-broker.http
   :code:

This framework by itself is visible to everyone in public API.

.. note::
    For `ProcuringEntity` with `defense` kind ``restricted_derivatives`` field will be set to ``true`` automatically.

The second step is moving the framework to `active` status:

.. http:example:: http/restricted/framework-activate-broker.http
   :code:

Create and activate Submissions with restricted access
------------------------------------------------------

After activating framework, users can register their submissions in period from `framework.period.startDate` to `framework.period.endDate`.

Let's register submission:

.. http:example:: http/restricted/submission-register-broker.http
   :code:

You can see that ``restricted`` field was set to ``true`` in ``config`` section of submission creation response.

Next activate submission:

.. http:example:: http/restricted/submission-activate-broker.http
   :code:

Request submissions with restricted access
------------------------------------------

Let's check submissions:

Anonymous
*********

Let's get submission with anonymous request:

.. http:example:: http/restricted/submission-get-anonymous.http
   :code:

We can see that some of it's fields are masked.

Let's check submission feed with anonymous request:

.. http:example:: http/restricted/submission-feed-anonymous.http
   :code:

Broker
******

But if we will make a request with `broker` token, we will see that corresponding fields are not longer masked:

.. http:example:: http/restricted/submission-get-broker.http
   :code:

Let's check submission feed for broker:

.. http:example:: http/restricted/submission-feed-broker.http
   :code:

Request Qualifications with restricted access
---------------------------------------------

Let's check qualification:

Anonymous
*********

Let's qualification with anonymous request:

.. http:example:: http/restricted/qualification-get-anonymous.http
   :code:

We can see that some of it's fields are masked.

Let's check qualification feed with anonymous request:

.. http:example:: http/restricted/qualification-feed-anonymous.http
   :code:

Broker
******

But if we will make a request with `broker` token, we will see that corresponding fields are not longer masked:

.. http:example:: http/restricted/qualification-get-broker.http
   :code:

Let's check qualification feed for broker:

.. http:example:: http/restricted/submission-feed-broker.http
   :code:

Activate Qualifications with restricted access
----------------------------------------------

Let's check current framework

.. http:example:: http/restricted/framework-with-agreement.http
   :code:

Let's activate qualification:

.. http:example:: http/restricted/qualification-activate-broker.http
   :code:

You can see that `agreementID` appeared in current framework, so let's check that agreement.

Request Agreement with restricted access
---------------------------------------------

Let's check agreement:

Anonymous
*********

Let's get agreement with anonymous request:

.. http:example:: http/restricted/agreement-get-anonymous.http
   :code:

We can see that some of it's fields are masked.

Let's check agreement feed with anonymous request:

.. http:example:: http/restricted/agreement-feed-anonymous.http
   :code:

Broker
******

But if we will make a request with `broker` token, we will see that corresponding fields are not longer masked:

.. http:example:: http/restricted/agreement-get-broker.http
   :code:

Let's check agreement feed for broker:

.. http:example:: http/restricted/agreement-feed-broker.http
   :code:

Masking rules
-------------

.. note::
    Rules are made of JSONPath expressions. For more info read `JSONPath specification <https://goessner.net/articles/JsonPath/>`_.

Rules for submission masking:

.. csv-table::
   :file: csv/restricted/submission-mask-mapping.csv
   :header-rows: 1

Rules for qualification masking:

.. csv-table::
   :file: csv/restricted/qualification-mask-mapping.csv
   :header-rows: 1

Rules for agreement masking:

.. csv-table::
   :file: csv/restricted/agreement-mask-mapping.csv
   :header-rows: 1
