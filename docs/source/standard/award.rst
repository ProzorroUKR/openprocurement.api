
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

    absent in :ref:`limited`:
    
:title:
    string, multilingual
    
    |ocdsDescription|
    Award title.
    
:description:
    string, multilingual
    
    |ocdsDescription|
    Award description.
    
:status:
    string
    
    |ocdsDescription|
    The current status of the award drawn from the `awardStatus` codelist.

    Possible values are:

    * `pending` - the award is under review of qualification committee
    * `unsuccessful` - the award has been rejected by qualification committee
    * `active` - the tender is awarded to the bidder from the `bid_id`
    * `cancelled` - the award has been cancelled by complaint review body

:date:
    string, :ref:`Date`, auto-generated, read-only
    
    |ocdsDescription|
    The date of the contract award.
    
:value:
    :ref:`Value` object, auto-generated, read-only

    |ocdsDescription|
    The total value of this award.

    Differences in :ref:`defense`, :ref:`esco`, :ref:`openua` and :ref:`openeu`:

    List of :ref:`Value` objects, auto-generated, read-only

    Differences in :ref:`limited`:

    `Value` object

:suppliers:
    List of :ref:`BusinessOrganization` objects, auto-generated, read-only
    
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

    Differences in :ref:`limited`:

        Id of related :ref:`lot`. Only if `tender.procurementMethodType` is `negotiation` or `negotiation.quick`.


Additionally in :ref:`defense`, :ref:`esco`, :ref:`openua` and :ref:`openeu`:

:eligible:
    bool

    Confirms compliance of eligibility criteria set by the procuring entity in the tendering documents.

:qualified:
    bool

    Confirms the absence of grounds for refusal to participate in accordance with Article 17 of the Law of Ukraine "On Public Procurement".


Additionally in :ref:`limited`:

:subcontractingDetails:
    string

    The text field of any length that contains information about subcontractor.

:qualified:
    bool

    Confirms that Procuring entity has no grounds to reject a participant in accordance with Article 17 of the Law of Ukraine "On Public Procurement".

:requirementResponses:
        List of :ref:`RequirementResponse` objects.

Award workflow in :ref:`limited`:
---------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
         A -> B;
         A -> D;
         B -> C;
    }

\* marks initial state


Workflow in :ref:`openeu` and :ref:`esco`:
------------------------------------------

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
