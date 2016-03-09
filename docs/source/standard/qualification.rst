.. include:: defs.hrst

.. index:: Qualification
.. _qualification:

Qualification
=============

Schema
------

:id:
    string, auto-generated


:bidID:
    string, auto-generated

    Bid that this Qualification protocol relates to.

:lotID:
    string, auto-generated

    In Multilot tenders, lot that this Qualification protocol relates to.

:date:
    string, :ref:`Date`, auto-generated, read-only

    The date of the qualification.

:documents:
    List of :ref:`Document` objects

    Container for Qualification documentation, protocols, reasons for
    qualification or disqualification. Uploaded by tender committee.

:status:
    string

    Possible values are:

    * `pending`
    * `active`
    * `unsuccessful`
    * `cancelled`

Workflow
--------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
         A -> B;
         A -> C;
         A -> D;
         D -> C;
         B -> C;
    }

\* marks initial state

.. index:: Date, Document
