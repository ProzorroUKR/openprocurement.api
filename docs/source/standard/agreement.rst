.. index:: Agreement
.. _agreement:

Agreement
=========

Schema
------

:id:
    uid, required, auto-generated

:agreementID:
    string, auto-generated, read-only

:agreementNumber:
    string

:date:
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
    
Workflow
------

.. image:: images/agreementstatus.png
