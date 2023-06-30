.. _value_currency_equality:

valueCurrencyEquality
=====================

Field `valueCurrencyEquality` is a boolean field that turns off validation `currency of bid should be identical to currency of value of tender`.
It means that multi-currency is used in the procedure.

Possible values for `valueCurrencyEquality` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/value-currency-equality-values.csv
   :header-rows: 1

valueCurrencyEquality is `true`
-------------------------------

`valueCurrencyEquality:true` means that validation will work while registering a bid and the system will check whether the currency of the bid is identical to the currency of the expected value in the tender/lot.

Let's create a tender with lots with `valueCurrencyEquality` set to `true`:

.. http:example:: http/value-currency-equality-true-tender-lots-post.http
   :code:

And add bid to it with the different currency than the expected value in lot:

.. http:example:: http/value-currency-equality-true-tender-lots-add-invalid-bid.http
   :code:

In that case we will have error, that adding bid with the different currency is forbidden.

Let's add bid to tender with currency identical to the currency of the expected value in the tender/lot:

.. http:example:: http/value-currency-equality-true-tender-lots-add-valid-bid.http
   :code:

The participant submits an offer, where `bid:value:currency = tender:value:currency`, when trying to transfer another currency, the system issues an error.
Let's try to patch bid currency to another one and we will see error, that it is forbidden with this configuration.

.. http:example:: http/value-currency-equality-true-tender-lots-patch-bid.http
   :code:

valueCurrencyEquality is `false`
---------------------------------

`valueCurrencyEquality:false` means that currency validation will not work.

.. note::
    Multi-currency can be applied only with `hasAuction:false` and with `hasAwardingOrder:false` and with `hasValueRestriction:false`.

Let's create a tender with lots with `valueCurrencyEquality` set to `false`:

.. http:example:: http/value-currency-equality-false-tender-lots-post.http
   :code:

And add bid to it with the different currency than the expected value in lot:

.. http:example:: http/value-currency-equality-false-tender-lots-add-valid-bid.http
   :code:

In that case we won't see any error, as adding bid with the different currency is allowed with configuration `valueCurrencyEquality:false`.

The customer and the participant conclude the contract in the currency in which the offer was indicated by the participant.
Let's look at completed tender, awards and contracts value's currency are the same as they were at bid:

.. http:example:: http/value-currency-equality-false-tender-complete.http
   :code:
