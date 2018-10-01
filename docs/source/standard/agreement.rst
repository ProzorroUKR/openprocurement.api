.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Agreement
.. _Agreement:

Agreement
========

Schema
------

:id:
    uid, auto-generated

    |ocdsDescription|
    The identifier for this agreement.

:agreementId:
    string

:agreementNumber:
    string

:title:
    string

    |ocdsDescription|
    Agreement title

:title_en:
    string

    |ocdsDescription|
    Agreement title in english

:title_ru:
    string

    |ocdsDescription|
    Agreement title in russian

:description:
    string

    |ocdsDescription|
    Agreement description

:description_en:
    string

    |ocdsDescription|
    Agreement description in english

:description_ru:
    string

    |ocdsDescription|
    Agreement description in russian

:status:
    string, required

    |ocdsDescription|
    The current status of the agreement.

    Possible values are:

    * `active` - this agreement has been signed by all the parties, and is
      now legally in force.
    * `terminated` - this agreement was signed and in force, and has now come
      to a close.  This may be due to a successful completion of the agreement,
      or may be early termination due to some non-completion issue.

:period:
    :ref:`Period`

    |ocdsDescription|
    The start and end date for the agreement.

:items:
    List of :ref:`Item` objects, read-only

    |ocdsDescription|
    The goods, services, and any intangible outcomes in this agreement.

:procuringEntity:
   :ref:`ProcuringEntity`

   |ocdsDescription|
   The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.

:dateSigned:
    string, :ref:`date`, auto-generated, read-only

    |ocdsDescription|
    The date the agreement was signed. In the case of multiple signatures, the date of the last signature.

:documents:
    List of :ref:`Document` objects

    |ocdsDescription|
    All documents and attachments related to the agreement, including any notices.

:changes:
    List of :ref:`ChangeTaxRate`, :ref:`ChangeItemPriceVariation`, :ref:`ChangePartyWithdrawal` or :ref:`ChangeThirdParty` objects.

:contracts:
    List of :ref:`Contract`  objects.

:revisions:
    List of :ref:`Revision`  objects.

:terminationDetails:
    string, required for unsuccessful agreement

    Reasons for agreement termination. Presence of this field indicates that agreement is unsuccessful.


Workflow
--------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="terminated"]
         A -> B;
    }

\* marks initial state
