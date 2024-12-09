.. _frameworks_has_items:

hasItems
========

Field `hasItems` is the boolean field that defines if the framework should have items.

Possible values for `hasItems` field depends on `frameworkType` field:

.. csv-table::
   :file: csv/has-items-values.csv
   :header-rows: 1

hasItems is `false`
-------------------

`hasItems:false` means that items is not allowed for framework.

Let's create a framework with `hasItems` set to `false` with items:

.. http:example:: http/has-items-false-with-items-create.http
   :code:

And then activate it:

.. http:example:: http/has-items-false-with-items-activate-error.http
   :code:

We can see error that indicates that items are not allowed for framework with `hasItems` set to `false`.

Now let's create a framework with `hasItems` set to `false` without items:

.. http:example:: http/has-items-false-without-items-create.http
   :code:

And then activate it:

.. http:example:: http/has-items-false-without-items-activate-success.http
   :code:

We can see that framework created successfully without items.

hasItems is `true`
------------------

`hasItems:true` means that items are required for framework.

Let's create a framework with `hasItems` set to `true` without items:

.. http:example:: http/has-items-true-without-items-create.http
   :code:

And then activate it:

.. http:example:: http/has-items-true-without-items-activate-error.http
   :code:

We can see error that indicates that items are required for framework with `hasItems` set to `true`.

Now let's create a framework with `hasItems` set to `true` with items:

.. http:example:: http/has-items-true-with-items-create.http
   :code:

And then activate it:

.. http:example:: http/has-items-true-with-items-activate-success.http
   :code:

We can see that framework created successfully with items.

Later, when agreement is created, items will be transferred to agreement:

.. http:example:: http/has-items-true-with-items-agreement.http
   :code:
