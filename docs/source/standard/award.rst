.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Award
.. _award:

Award
=====

Schema
------

:id:
    string, auto-generated, read-only
    
    |ocdsDescription|
    The identifier for this award.
    
:bid_id:
    string, auto-generated, read-only

    The Id of a bid that the award relates to.
    
:title:
    string, multilingual
    
    |ocdsDescription|
    Award title.
    
:description:
    string, multilingual
    
    |ocdsDescription|
    Award description.

:eligible:
    bool

    Confirms compliance of eligibility criteria set by the procuring entity in the tendering documents.

:qualified:
    bool

    Confirms the absence of grounds for refusal to participate in accordance with Article 17 of the Law of Ukraine "On Public Procurement".

:status:
    string
    
    |ocdsDescription|
    The current status of the award drawn from the `awardStatus` codelist.

    Possible values are:

    * `pending` - the award is under review of qualification committee
    * `unsuccessful` - the award has been rejected by qualification comittee
    * `active` - the tender is awarded to the bidder from the `bid_id`
    * `cancelled` - the award has been cancelled by complaint review body

:date:
    string, :ref:`Date`, auto-generated, read-only
    
    |ocdsDescription|
    The date of the contract award.
    
:value:
    List of :ref:`Value` objects, auto-generated, read-only
    
    |ocdsDescription|
    The total value of this award.
    
:suppliers:
    List of :ref:`Organization` objects, auto-generated, read-only
    
    |ocdsDescription|
    The suppliers awarded with this award.
    
:items:
    List of :ref:`Item` objects, auto-generated, read-only
    
    |ocdsDescription|
    The goods and services awarded in this award, broken into line items wherever possible. Items should not be duplicated, but the quantity specified instead. 
    
:documents:
    List of :ref:`Document` objects
    
    |ocdsDescription|
    All documents and attachments related to the award, including any notices. 
    
:complaints:
    List of :ref:`Complaint` objects

:complaintPeriod:
    :ref:`period`

    The timeframe when complaints can be submitted.

:lotID:
    string

    Id of related :ref:`lot`.


Workflow
--------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
         A -> B;
         A -> D;
         B -> C;
         D -> C;
    }

\* marks initial state
