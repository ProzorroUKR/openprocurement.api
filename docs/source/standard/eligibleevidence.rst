
.. include:: defs.hrst

.. index:: EligibleEvidence
.. _EligibleEvidence:

EligibleEvidence
================

Schema
------

:id:
    uid, auto-generated

:title:
    string, multilingual, required

    |ocdsDescription|
    EligibleEvidence title.

:description:
    string, multilingual

    |ocdsDescription|
    EligibleEvidence description.

:type:
    string

    |ocdsDescription|
    the form in which the buyer wants to obtain evidence.

    Possible values are:
     :`document`:
       An internal document stored in Prozorro system
     :`statement`:
       A machine-readable confirmation by a requested Party
