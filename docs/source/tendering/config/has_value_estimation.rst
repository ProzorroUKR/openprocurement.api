.. _has_value_estimation:

hasValueEstimation
==================

Field `hasValueEstimation` is a boolean field that determines the presence or absence of the expected cost in the procurement.

Possible values for `hasValueEstimation` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/has-value-estimation-values.csv
   :header-rows: 1

hasValueEstimation is `true`
-----------------------------

`hasValueEstimation:true` means that procurement has the expected cost.

Let's create a tender with `hasValueEstimation` set to `true`:

.. http:example:: http/has-value-estimation-true-tender-lots-post.http
   :code:

Tender created successfully with expected cost of the procurement.

And add lot to it:

.. http:example:: http/has-value-estimation-true-tender-lots-add-post.http
   :code:

Lot added successfully with expected lot value.

Let's look at the tender:

.. http:example:: http/has-value-estimation-true-tender-lots-add-post.http
   :code:

hasValueEstimation is `false`
-------------------------------

`hasValueEstimation:false` means that procurement does not have the expected cost. System will reject tender expected cost, if it will be passed.

Let's create a tender with `hasValueEstimation` set to `false` and expected cost:

.. http:example:: http/has-value-estimation-false-tender-lots-post-invalid.http
   :code:

In that case we will have error, tender with expected cost value is forbidden.

Let's create a tender with `hasValueEstimation` set to `false` without expected cost:

.. http:example:: http/has-value-estimation-false-tender-lots-post.http
   :code:

The same rule for lots. System will reject lots with expected cost.

Let's add a lot with expected cost:

.. http:example:: http/has-value-estimation-false-tender-lots-add-post-invalid.http
   :code:

In that case we will have error, lots with expected cost value is forbidden.

Let's add a lot without expected cost:

.. http:example:: http/has-value-estimation-false-tender-lots-add-post.http
   :code:

And finally look at the tender:

.. http:example:: http/has-value-estimation-false-tender-complete.http
   :code:

Difference
----------

Differences for tender with `hasValueEstimation` set to `false` comparing to `true` are:

* tenders have no `value:amount`, it's forbidden

* lots have no `value:amount`, it's also forbidden
