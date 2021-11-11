.. include:: defs.hrst

.. index:: Agreement
.. _agreement:

Agreement in :ref:`frameworks_electroniccatalogue`
==================================================

Schema
------

:id:
    uid, required, auto-generated

:agreementID:
    string, auto-generated, read-only

:agreementType:
    string, auto-generated, value: `electronicCatalogue`, read-only

:status:
    string

     The current status of agreement.
     Possible values are:

    * `active`
    * `terminated`

:date:
    string, :ref:`date`, auto-generated, read-only

    The date of the agreement change status.

:dateModified:
    string, :ref:`date`, auto-generated, read-only

    The date of the agreement change.

:procuringEntity:
   :ref:`ProcuringEntity`, auto-generated from framework, read-only

   Organization conducting the agreement.

:period:
    :ref:`Period`

    The timeframe when agreement is in force.

:classification:
   :ref:`Classification`, required, auto-generated from framework, read-only

:additionalClassifications:
    List of :ref:`Classification` objects, auto-generated from framework, read-only

:contracts:
    List of :ref:`Contract` objects

:frameworkDetails:
    string


.. _agreement_cfaua:

Agreement in :ref:`cfaua`
=========================

Schema
------

:id:
    uid, required, auto-generated

:agreementID:
    string, auto-generated, read-only

:agreementNumber:
    string

:agreementType:
    string, value: `cfaua`

:changes:
    List of :ref:`ChangeTaxRate`, :ref:`ChangeItemPriceVariation`, :ref:`ChangePartyWithdrawal` or :ref:`ChangeThirdParty` objects.

    Only in `agreements` container.

:date:
    string, :ref:`date`, auto-generated, read-only
    
    The date of the agreement change.

:dateModified:
    string, :ref:`date`, auto-generated, read-only

    The date of the agreement change.

:dateSigned:
    string, :ref:`date`
    
    The date of the agreement signed.

:description:
    string, multilingual
    
    Agreement description

:description_en:
    string, multilingual
    
    Agreement description

:description_ru:
    string, multilingual
    
    Agreement description

:documents:
    List of :ref:`Document` objects
    
    |ocdsDescription|
    All documents and attachments related to the agreement, including any notices.

:items:
    List of :ref:`Item` objects

:period:
    :ref:`Period`
    
    The timeframe when agreement is in force. Maximum 4 years.
    
    :clarificationsUntil: 
    
    Deadline for participants to submit price documents

:status:
    string

     The current status of agreement.
     Possible values are:

    * `pending` - the agreement is under signing between procuring entity and :ref:`Contract` 
    * `unsuccessful` - the agreement has not been signed between procuring entity and :ref:`Contract`
    * `active` - the agreement is signed between procuring entity and :ref:`Contract`
    * `cancelled` - the agreement has been cancelled within cancellation of tender/lot.

     Different in `agreement` container:

    * `active` - the agreement is active and can be used for creating `selection` procedure
    * `terminated` - the agreement is cannot be used, for creating `selection` procedure

    
:contracts:
    List of :ref:`Contract` objects

:title:
    string, required
    
    Agreement title

:title_ru:
    string, required
    
    Agreement title

:title_en:
    string, required
    
    Agreement title

.. _agreement_pricequotation:

Agreement in :ref:`pricequotation`
==================================

Schema
------

:id:
    uid, required

    ID for related Agreement from :ref:`frameworks_electroniccatalogue`


Workflow
--------

.. graphviz::

    digraph G {
        A [ label="pending" ]
        B [ label="active" ]
        C [ label="cancelled" ]
        D [ label="unsuccessful"]
         A -> B;
         A -> C;
         A -> D;
    }

Workflow in :ref:`agreementcfaua`
---------------------------------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="terminated"]
         A -> B;
    }

\* marks initial state
