
.. include:: defs.hrst

.. index:: SignerInfo

.. _SignerInfo:

SignerInfo
==========

Schema
------

:name:
    string, required

    |ocdsDescription|
    signer fullname.

:email:
    string, required

    |ocdsDescription|
    The e-mail address of the signer.

:telephone:
    string, required

    |ocdsDescription|
    The telephone number of the signer. This should include the international dialling code.


:iban:
    string, required

    |ocdsDescription|
    The bank account number of the signatory.


:basisOf:
    string, required

    |ocdsDescription|
    name of the document on the basis of which the signatory acts


:position:
    string, required

    |ocdsDescription|
    position of the signer in the organisation.
