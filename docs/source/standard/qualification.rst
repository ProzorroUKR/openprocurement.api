.. include:: defs.hrst

.. index:: Qualification
.. _qualification:

Qualification
=============

Schema
------

:id:
    string, auto-generated

:title:
    string, multilingual

    |ocdsDescription|
    Qualification title.

:description:
    string, multilingual

    |ocdsDescription|
    Qualification description.

:eligible:
    bool

    Confirms compliance of eligibility criteria set by the procuring entity in the tendering documents.

:qualified:
    bool

    Confirms the absence of grounds for refusal to participate in accordance with Article 17 of the Law of Ukraine "On Public Procurement".

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

:complaints:
    List of :ref:`Complaint` and :ref:`Claim` objects.

:status:
    string

    Possible values are:

    * `pending` - waiting for qualification
    * `active` - qualification has been confirmed
    * `unsuccessful` - participant didn't pass qualification
    * `cancelled`- qualification decision has been cancelled

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
