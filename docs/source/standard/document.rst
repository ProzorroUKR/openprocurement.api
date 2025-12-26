
.. include:: defs.hrst

.. index:: Document, Attachment, File, Notice, Bidding Documents, Technical Specifications, Evaluation Criteria, Clarifications

.. _Document:

Document
========

Схема
-----

:id:
    рядок, генерується автоматично

:documentType:
    рядок

    Можливі значення для файлів підпису (ЕЦП):

    * `notice` - **Файл підпису оголошення закупівлі/підтвердження кваліфікації**

      Використовується в документах до :ref:`tender` та :ref:`award`.

    * `evaluationReports` - **Файл підпису звіту про оцінку**

      Використовується в документах до :ref:`tender` та :ref:`framework_qualification` у фреймворках.

    * `proposal` - **Файл підпису підтвердження пропозиції**

      Використовується в документах до :ref:`bid`

    * `extensionReport` - **Файл підпису для продовження строку розгляду award**

      Використовується в документах до :ref:`award`.

    * `deviationReport` - **Файл підпису для протоколу виправлення невідповідностей (24 години) в award/qualification***

      Використовується в документах до :ref:`qualification` та :ref:`award`.

    Можливі значення :ref:`tender`: `типи документів для зкупівлі. <https://github.com/ProzorroUKR/standards/blob/master/document_types/tender.json>`_
                                                                                                                                                  
    
    Можливі значення :ref:`award`: `типи документів для авардів. <https://github.com/ProzorroUKR/standards/blob/master/document_types/award.json>`_

    
    Можливі значення :ref:`contract`: `типи документів для контрактів. <https://github.com/ProzorroUKR/standards/blob/master/document_types/contract.json>`_
                                                                                                                                                        
    
    Можливі значення :ref:`bid`: `типи документів для пропозиції. <https://github.com/ProzorroUKR/standards/blob/master/document_types/bid.json>`_


    Можливі значення для :ref:`agreement`


        * `notice` - **Повідомлення про Рамкову угоду**

          БІЛЬШЕ НЕ ВИКОРИСТОВУЄТЬСЯ. Зараз цей тип документу використовується в якості файлу підпису.

          Раніше цей тип документу використовувався як офіційне повідомлення, що містить деталі підписання договору та початку його реалізації. Це може бути посилання на документ, веб-сторінку, чи на офіційний бюлетень, де розміщено повідомлення.

        * `contractSigned` - **Підписана Рамкова угода**

        * `contractArrangements` - **Заходи для припинення Рамкової угоди**

        * `contractSchedule` - **Розклад та етапи**

        * `contractAnnexe` - **Додатки до Рамкової угоди**

        * `contractGuarantees` - **Забезпечення тендерних пропозицій**

        * `subContract` - **Субпідряд**

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
                              
    |ocdsDescription| Пряме посилання на документ чи додаток. 
    
:datePublished:
    рядок, :ref:`date`
                  
    |ocdsDescription| Дата, коли документ був опублікований вперше. 
    
:dateModified:
    рядок, :ref:`date`
                  
    |ocdsDescription| Дата, коли документ був змінений востаннє
                                                           
:language:
    рядок

    Можливі значення:

    * `uk`
    * `en`
    * `ru`
    
    |ocdsDescription| Вказує мову документа, використовуючи або двоцифровий код `ISO 639-1 <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_, або розширений `BCP47 language tags <http://www.w3.org/International/articles/language-tags/>`_. 

:documentOf:
    рядок

    Можливі значення:

    * `tender`
    * `contract`
    * `change`
    * `item`
    * `lot`

:relatedItem:
    рядок

    ID пов’язаних :ref:`contract`, :ref:`change`, :ref:`lot` або :ref:`item`.

