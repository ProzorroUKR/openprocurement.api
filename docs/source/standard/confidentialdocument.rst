
.. include:: defs.hrst

.. index:: Document, Attachment, File, Notice, Bidding Documents, Technical Specifications, Evaluation Criteria, Clarifications

.. _ConfidentialDocument:

ConfidentialDocument
====================

Схема
-----

:id:
    рядок, генерується автоматично

:documentType:
    рядок

    Можливі значення :ref:`tender`: `типи документів для зкупівлі. <https://github.com/ProzorroUKR/standards/blob/master/document_types/tender.json>`_


    Можливі значення :ref:`award`: `типи документів для авардів. <https://github.com/ProzorroUKR/standards/blob/master/document_types/award.json>`_


    Можливі значення :ref:`contract`: `типи документів для контрактів. <https://github.com/ProzorroUKR/standards/blob/master/document_types/contract.json>`_


    Можливі значення :ref:`bid`: `типи документів для пропозиції. <https://github.com/ProzorroUKR/standards/blob/master/document_types/bid.json>`_


:title:
    рядок, багатомовний
                   
    |ocdsDescription| Назва документа. 
    
:description:
    рядок, багатомовний
                   
    |ocdsDescription| Короткий опис документа. Якщо документ не буде доступний онлайн, то поле опису можна використати для вказання способу отримання копії документа.
                                                                                                                                                                  
:format:
    рядок
     
    |ocdsDescription| Формат документа зі `списку кодів IANA Media Types <http://www.iana.org/assignments/media-types/>`_, з одним додатковим значенням 'offline/print', що буде використовуватись, коли запис цього документа використовується для опису офлайнової публікації документа. 
    
:url:
    рядок, генерується автоматично
                              
    |ocdsDescription| Пряме посилання на документ або додаток. 

:confidentiality:
    рядок
     
    Можливі значення:

    * `public` - публічний документ
    * `buyerOnly` - приватний документ

:confidentialityRationale:
    рядок
     
    Причина для конфіденційності документів.
                                        
:datePublished:
    рядок, :ref:`date`
                  
    |ocdsDescription| Дата, коли документ був опублікований вперше. 
    
:dateModified:
    рядок, :ref:`date`
                  
    |ocdsDescription| Дата, коли документ був змінений востаннє
                                                           
:language:
    рядок, значення за замовчуванням - `uk`

    Можливі значення:

    * `uk`
    * `en`
    * `ru`
    
    |ocdsDescription| Вказує мову документа, використовуючи або двоцифровий код `ISO 639-1 <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_, або розширений `BCP47 language tags <http://www.w3.org/International/articles/language-tags/>`_. 

:documentOf:
    рядок

    Можливі значення:

    * `tender`
    * `item`
    * `lot`

    Для :ref:`Complaint` також можливе значеня:

    * `post`

:relatedItem:
    рядок

    Ідентифікатор пов'язаних об'єктів :ref:`lot` або :ref:`item`.

Additionally in :ref:`competitivedialogue` (first stage):

:isDescriptionDecision:
    bool

    |ocdsDescription| Make document "Description of the decision to purchase".
