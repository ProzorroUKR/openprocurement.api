.. _has_value_restriction:

hasValueRestriction
====================

Field `hasValueRestriction` is a boolean field that indicates whether the bid value can exceed tender/lot initial value of the subject of procurement, specified in the announcement.

Possible values for `hasValueRestriction` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/has-value-restriction-values.csv
   :header-rows: 1

hasValueRestriction is `true`
-----------------------------

`hasValueRestriction:true` means that bid value can not exceed initial value of the subject of procurement.

Let's create a tender with lots with `hasValueRestriction` set to `true`:

.. http:example:: http/has-value-restriction-true-tender-lots-post.http
   :code:

And add bid to it with value more than initially announced in lot:

.. http:example:: http/has-value-restriction-true-tender-lots-add-invalid-bid.http
   :code:

In that case we will have error, that adding bid with exceeded value is forbidden.

Let's add bid to tender with value less than initially announced in lot:

.. http:example:: http/has-value-restriction-true-tender-lots-add-valid-bid.http
   :code:

Let's try to patch bid value to bigger one and we will see error, that it is forbidden with this configuration.

.. http:example:: http/has-value-restriction-true-tender-lots-patch-bid.http
   :code:


hasValueRestriction is `false`
-------------------------------

`hasValueRestriction:false` means that bid value can exceed initial value of the subject of procurement.


Let's create a tender with lots with `hasValueRestriction` set to `false`:

.. http:example:: http/has-value-restriction-false-tender-lots-post.http
   :code:

And add bid to it with value more than initially announced in lot:

.. http:example:: http/has-value-restriction-false-tender-lots-add-valid-bid.http
   :code:

In that case we won't see any error, as adding bid with exceeded value is allowed with configuration `hasValueRestriction:false`.
