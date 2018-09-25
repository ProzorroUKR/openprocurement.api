.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Document, Attachment, File, Notice, Bidding Documents, Technical Specifications, Evaluation Criteria, Clarifications

.. _Document:

Document
========

Schema
------

:id:
    string, auto-generated

:documentType:
    string

     Possible values for :ref:`contract`
    
    
    * `notice` - **Contract notice**
    
        The formal notice that gives details of a contract being signed and valid to start implementation. This may be a link to a downloadable document, to a web page, or to an official gazette in which the notice is contained.
    
    * `contractSigned` - **Signed Contract**
    
    * `contractArrangements` - **Arrangements for ending contract**
    
    * `contractSchedule` - **Schedules and milestones**
    
    * `contractAnnexe` - **Annexes to the Contract**
    
    * `contractGuarantees` - **Guarantees**
    
    * `subContract` - **Subcontracts**
    

:title:
    string, multilingual
    
    |ocdsDescription|
    The document title. 
    
:description:
    string, multilingual
    
    |ocdsDescription|
    A short description of the document. In the event the document is not accessible online, the description field can be used to describe arrangements for obtaining a copy of the document.
    
:format:
    string
    
    |ocdsDescription|
    The format of the document taken from the `IANA Media Types code list <http://www.iana.org/assignments/media-types/>`_, with the addition of one extra value for 'offline/print', used when this document entry is being used to describe the offline publication of a document. 
    
:url:
    string, auto-generated
    
    |ocdsDescription|
    Direct link to the document or attachment. 
    
:datePublished:
    string, :ref:`date`
    
    |ocdsDescription|
    The date on which the document was first published. 
    
:dateModified:
    string, :ref:`date`
    
    |ocdsDescription|
    Date that the document was last modified
    
:language:
    string

    Possible values are:

    * `uk`
    * `en`
    * `ru`
    
    |ocdsDescription|
    Specifies the language of the linked document using either two-digit `ISO 639-1 <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_, or extended `BCP47 language tags <http://www.w3.org/International/articles/language-tags/>`_. 

:documentOf:
    string

    Possible values are:

    * `tender`
    * `item`
    * `contract`
    * `agreement`
    * `lot`
    * `change`

:relatedItem:
    string

    Id of related :ref:`tender`, :ref:`item`, :ref:`contract`, :ref:`agreement`, :ref:`change` or :ref:`item`.
