
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

    Possible values for sign documents:

    * `notice` - **Sign document for publication tender/confirming qualification**

      Can be used in :ref:`tender` and :ref:`award`.

    * `evaluationReports` - **Sign document for evaluation report**

      Can be used in :ref:`tender` and :ref:`framework_qualification` in framework.

    * `proposal` - **Proposal**

      Can be used in  :ref:`bid`

    Possible values for :ref:`tender`: `tender document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/tender.json>`_
    
    
    Possible values for :ref:`award`: `award document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/award.json>`_

    
    Possible values for :ref:`contract`: `contract document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/contract.json>`_
    
    
    Possible values for :ref:`bid`: `bid document types. <https://github.com/ProzorroUKR/standards/blob/master/document_types/bid.json>`_


    Possible values for :ref:`agreement`


        * `notice` - **Framework agreement notice**

          NOT USED ANYMORE. Now it's use as sign document.

          Earlier this type of document was used as the formal notice that gives details of a contract being signed and valid to start implementation. This may be a link to a downloadable document, to a web page, or to an official gazette in which the notice is contained.

        * `contractSigned` - **Signed Framework agreement**

        * `contractArrangements` - **Arrangements for ending Framework agreement**

        * `contractSchedule` - **Schedules and milestones**

        * `contractAnnexe` - **Annexes to the Framework agreement**

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
    * `contract`
    * `change`
    * `item`
    * `lot`

:relatedItem:
    string

    Id of related :ref:`contract`, :ref:`change`, :ref:`lot` or :ref:`item`.

