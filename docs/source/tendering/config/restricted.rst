.. _restricted:

restricted
==========

Restricted tender
-----------------

Field `restricted` is a boolean field that indicates whether the tender has restricted access.

Let's create tender with configuration `restricted=false`:

.. http:example:: http/restricted-false-tender-post.http
   :code:

Then after activation let's make an anonymous get request:

.. http:example:: http/restricted-false-tender-get-anon.http
   :code:

We can see that this tender has usual representation.

Now lets create tender with configuration `restricted=true`:

.. http:example:: http/restricted-true-tender-post.http
   :code:

Then after activation let's make an anonymous get request:

.. http:example:: http/restricted-true-tender-get-anon.http
   :code:

Now we can see that some of it's fields are masked.

But if we will make a request with `broker` token, we will see that corresponding fields are not longer masked:

.. http:example:: http/restricted-true-tender-get.http
   :code:

Lets look at those 2 tenders in feed.

With anonymous request:

.. http:example:: http/restricted-tender-feed-anon.http
   :code:

With broker request:

.. http:example:: http/restricted-tender-feed.http
   :code:

We can also see that `restricted=true` tender is masked for anonymous request but not for broker request.

Restricted contract
-------------------

For tender with `restricted=true` contract also will be created with `restricted=true`.

Let's get restricted contract with anonymous request:

.. http:example:: http/restricted-true-contract-get-anon.http
   :code:

We can see that some of it's fields are masked.

But if we will make a request with `broker` token, we will see that corresponding fields are not longer masked:

.. http:example:: http/restricted-true-contract-get.http
   :code:

Masking rules
-------------

.. note::
    Rules are made of JSONPath expressions. For more info read `JSONPath specification <https://goessner.net/articles/JsonPath/>`_.

Rules for tender masking:

.. csv-table::
   :file: csv/tender-mask-mapping.csv
   :header-rows: 1

Rules for contract masking:

.. csv-table::
   :file: csv/contract-mask-mapping.csv
   :header-rows: 1
