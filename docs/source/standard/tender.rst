.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Tender
.. _tender:

Tender
======

Schema
------

:title:
   string, multilingual

   The name of the tender, displayed in listings. You can include the following items:

   * tender code (in procuring organization management system)
   * periodicity of the tender (annual, quarterly, etc.)
   * item being procured
   * some other info

:description:
   string, multilingual

   Detailed description of tender.

:tenderID:
   string, auto-generated, read-only

   The tender identifier that can be used to find tender in "paper" documentation.

   |ocdsDescription|
   TenderID should always be the same as the OCID. It is included to make the flattened data structure more convenient.

:procuringEntity:
   :ref:`ProcuringEntity`, required

   Organization conducting the tender.

   |ocdsDescription|
   The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.

   If :code:`procurementMethodType` is :code:`negotiation` or :code:`negotiation.quick`, then possible values of :code:`ProcuringEntity.kind` are limited to :code:`['general', 'special', 'defense']`.

:value:
   :ref:`value`, required

   Total available tender budget.

   |ocdsDescription|
   The total estimated value of the procurement.

:items:
   list of :ref:`item` objects, required

   List that contains single item being procured.

   |ocdsDescription|
   The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.


:documents:
   List of :ref:`document` objects

   |ocdsDescription|
   All documents and attachments related to the tender.

:awards:
    List of :ref:`award` objects

    All qualifications (disqualifications and awards).

:contracts:
    List of :ref:`Contract` objects


   |ocdsDescription|
   The date or period on which an award is anticipated to be made.

:status:
   string

   :`active`:
       Active tender (default)
   :`complete`:
       Completed tender
   :`cancelled`:
       Cancelled tender
   :`unsuccessful`:
       Unsuccessful tender

   Status of the Tender.

:cancellations:
   List of :ref:`cancellation` objects.

   Contains 1 object with `active` status in case of cancelled Tender.

   The :ref:`cancellation` object describes the reason of tender cancellation contains accompanying
   documents  if any.

:procurementMethod:
    string, auto-generated

    :`limited`:
        Default.
        
    Procurement Method of the Tender.

:procurementMethodRationale:
    string, multilingual

    Procurement Method Rationale of tender.

:procurementMethodType:
    string 

    :`reporting`:
        reporting procedure indentifier

    :`negotiation`:
        negotiation procedure indentifier

    :`negotiation.quick`:
        negotiation.quick procedure indentifier

:dateModified:
    string, :ref:`date`


:owner:
    string, auto-generated

:cause:
   string, required for **negotiation** procedure/ optional for **negotiation.quick** procedure
    
   Causes for using negotiation or negotiation.quick procedures. For more details see Article 35 of the Law of Ukraine "On Public Procurement".

       Possible values for **negotiation** and **negotiation.quick** procedure:
        
   * `artContestIP`
   Purchase of art or intellectual property

   * `noCompetition`
   Lack of competition

   * `twiceUnsuccessful`
   Two tenders have already been cancelled due to lack of participants

   * `additionalPurchase`
   Need to use the same supplier for unification, standardization, etc.

   * `additionalConstruction`
   Need of additional construction works

   * `stateLegalServices`
   Purchase of legal services connected with protection of rights and interests of Ukraine

    Possible values for **negotiation.quick** procedure:

   * `quick`
   Procurement is urgent
    
:causeDescription:
   string, multilingual, required for **negotiation** and **negotiation.quick** procedures
    
   Reasoning behind usage of negotiation or negotiation.quick procedures.

:lots:
   List of :ref:`lot` objects.

   Contains all tender lots.
   Only if `tender.procurementMethodType` is `negotiation` or `negotiation.quick`.

Tender workflow
---------------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="complete"]
        C [ label="cancelled"]
         A -> B;
         A -> C;
    }

\* marks initial state
