
.. include:: defs.hrst

.. index:: Evidence
.. _evidence:

Evidence
========

Schema
------

:id:
    uid, auto-generated

:title:
    string, multilingual

    |ocdsDescription|
    Evidence title.

:description:
    string, multilingual

    |ocdsDescription|
    Evidence description.

:type:
    string

    |ocdsDescription|
    the form in which the bidder give evidence.

    Possible values are:
     :`document`:
       An internal document stored in Prozorro system
     :`statement`:
       A machine-readable confirmation by a requested Party

:relatedDocument:
    :ref:`Reference`

    |ocdsDescription|
    The reference for bid/award document.
