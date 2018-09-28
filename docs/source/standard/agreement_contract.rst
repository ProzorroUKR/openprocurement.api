.. include:: defs.hrst

.. index:: AgreementContract
.. _AgreementContract:

AgreementContract
=================

Schema
------

:id:
    uid, auto-generated, read-only

:awardID:
    string, auto-generated, read-only

:bidID:
    string

:parameters:
    List of :ref:`Parameter` objects, auto-generated, read-only

:suppliers:
    List of :ref:`Organization` objects, auto-generated, read-only

:status:
    string, required
    
    Possible values are:
    
    * `active` - participant signed the agreement
    * `unsuccessful` - participant refused to sign the agreement

:date:
    string, :ref:`date`

    The date when the contract was changed or activated.

:bidID:
    string, auto-generated, read-only
    
    Contract related :ref:`Bid`


:unitPrices:
    List of :ref:`UnitPrice`
    
    Contract prices per :ref:`Item`