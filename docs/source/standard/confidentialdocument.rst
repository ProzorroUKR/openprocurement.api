
.. include:: defs.hrst

.. index:: Document, Attachment, File, Notice, Bidding Documents, Technical Specifications, Evaluation Criteria, Clarifications

.. _ConfidentialDocument:

ConfidentialDocument
====================

Schema
------

:id:
    string, auto-generated

:documentType:
    string

    Possible values for :ref:`tender`: `tender document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/tender.json>`_


    Possible values for :ref:`award`: `award document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/award.json>`_


    Possible values for :ref:`contract`: `contract document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/contract.json>`_


    Possible values for :ref:`bid`: `bid document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/bid.json>`_


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

:confidentiality:
    string
    
    Possible values are:

    * `public`
    * `buyerOnly`

:confidentialityRationale:
    string
        
    Reasons for confidentiality of documents.
    
:datePublished:
    string, :ref:`date`
    
    |ocdsDescription|
    The date on which the document was first published. 
    
:dateModified:
    string, :ref:`date`
    
    |ocdsDescription|
    Date that the document was last modified
    
:language:
    string, default = `uk`

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
    * `lot`

    For :ref:`Complaint` it is also allowed to choose:

    * `post`

:relatedItem:
    string

    ID of related :ref:`lot` or :ref:`item`.

Additionally in :ref:`competitivedialogue` (first stage):

:isDescriptionDecision:
    bool

    |ocdsDescription|
    Make document "Description of the decision to purchase".
