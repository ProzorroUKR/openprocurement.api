
.. include:: defs.hrst

.. index:: Organization, Company

.. _Organization:

Organization
============

Схема
-----

:name:
    рядок, багатомовний

    Додатково у :ref:`openeu` та :ref:`esco`:

    uk (name) та en (name_en) переклади обов’язкові
                                               
    |ocdsDescription| Назва організації.
                                    
:identifier:
    :ref:`Identifier`
                 
    |ocdsDescription| Ідентифікатор цієї організації. 
    
:additionalIdentifiers:
    Список об’єктів :ref:`identifier`

:address:
    :ref:`Address`, обов’язково

:contactPoint:
    :ref:`ContactPoint`, обов’язково

Додатково у :ref:`openeu`:

:additionalContactPoints:
    Список об’єктів :ref:`ContactPoint`


.. index:: BusinessOrganization, Company

.. _BusinessOrganization:

BusinessOrganization
====================

Схема
-----

:name:
    рядок, багатомовний

    Додатково у :ref:`openeu` та :ref:`esco`:

    uk (name) та en (name_en) переклади обов’язкові

    |ocdsDescription| Назва організації.

:identifier:
    :ref:`Identifier`

    |ocdsDescription| Ідентифікатор цієї організації.

:additionalIdentifiers:
    Список об’єктів :ref:`identifier`

:address:
    :ref:`Address`, обов’язково

:contactPoint:
    :ref:`ContactPoint`, обов’язково

Додатково у :ref:`openeu`:

:additionalContactPoints:
    Список об’єктів :ref:`ContactPoint`

:scale:
    рядок, обов’язковий

    Можливі значення:

    * `micro`
    * `sme`
    * `large`
    * `mid`
    * `not specified`

    Validation depends on:

        * :ref:`ORGANIZATION_SCALE_FROM` constant


.. index:: Tenderer, Company

.. _Tenderer:

Tenderer
========

Схема
-----

:name:
    рядок, багатомовний

    Додатково у :ref:`openeu` та :ref:`esco`:

    uk (name) та en (name_en) переклади обов’язкові

    |ocdsDescription| Назва організації.

:identifier:
    :ref:`Identifier`

    |ocdsDescription| Ідентифікатор цієї організації.

:additionalIdentifiers:
    Список об’єктів :ref:`identifier`

:address:
    :ref:`Address`, обов’язково

:contactPoint:
    :ref:`ContactPoint`, обов’язково

:signerInfo:
    :ref:`SignerInfo`

:contract_owner:
    рядок

    Може бути вказаний один з майданчиків, який отримав 6 рівень акредитації

Додатково у :ref:`openeu`:

:additionalContactPoints:
    Список об’єктів :ref:`ContactPoint`

:scale:
    рядок, обов’язковий

    Можливі значення:

    * `micro`
    * `sme`
    * `large`
    * `mid`
    * `not specified`

    Validation depends on:

        * :ref:`ORGANIZATION_SCALE_FROM` constant


.. index:: Buyer

.. _Buyer:


Buyer
=====

Схема
-----

:name:
    рядок, багатомовний

    |ocdsDescription| Назва організації.

:identifier:
    :ref:`Identifier`

    |ocdsDescription| Ідентифікатор цієї організації.

:address:
    :ref:`Address`, обов’язково

:contactPoint:
   :ref:`ContactPoint`, optionally can be added to buyers only

:kind:
    рядок

    Можливі значення:
        - ``authority`` - Орган державної влади, місцевого самоврядування або правоохоронний орган
        - ``central`` - Юридична особа, що здійснює закупівлі в інтересах замовників (ЦЗО)
        - ``defense`` - Замовник, що здійснює закупівлі для потреб оборони
        - ``general`` - Юридична особа, яка забезпечує потреби держави або територіальної громади
        - ``other`` - Державне або комунальне підприємство, яке не належить до замовників
        - ``social`` - Орган соціального страхування
        - ``special`` - Юридична особа, яка здійснює діяльність в одній або декількох окремих сферах господарювання

:signerInfo:
    :ref:`SignerInfo`

:contract_owner:
    рядок

    Може бути вказаний один з майданчиків, який отримав 6 рівень акредитації


.. index:: EContractOrganization, Company

.. _EContractOrganization:

EContractOrganization
=====================

Схема
-----

:name:
    рядок, багатомовний

    |ocdsDescription| Назва організації.

:identifier:
    :ref:`Identifier`

    |ocdsDescription| Ідентифікатор цієї організації.

:additionalIdentifiers:
    Список об’єктів :ref:`identifier`

:address:
    :ref:`Address`, обов’язково

:signerInfo:
    :ref:`SignerInfo`

:contract_owner:
    рядок

    Може бути вказаний один з майданчиків, який отримав 6 рівень акредитації


.. index:: Company, id

.. _Identifier:

Identifier
==========

Схема
-----

:scheme:
   рядок, обов’язковий(в об'єкті `Legislation` не обов'язковий)

   |ocdsDescription| Ідентифікатори організації беруться з існуючої схеми ідентифікації. Це поле вказує схему або список кодів, де можна знайти ідентифікатор організації. Це значення повинно братись зі Схеми Ідентифікації Організацій.

:id:
   рядок, обов’язковий
                   
   |ocdsDescription| Ідентифікатор організації у вибраній схемі.

   Дозволеними є коди зі `спику кодів "Organisation Registration Agency" Стандарту IATI <http://iatistandard.org/codelists/OrganisationRegistrationAgency/>`_ з додаванням коду `UA-EDR` для організацій, зареєстрованих в Україні (ЄДРПОУ та ІПН).

:legalName:
   рядок, багатомовний

   Додатково у :ref:`complaint` для поля `author`:

   uk (legalName) переклад обов’язковий. en (legalName_en), ru (legalName_ru) переклади не обов’язкові

   |ocdsDescription| Легально зареєстрована назва організації.

:uri:
   uri

   |ocdsDescription| URI для ідентифікації організації, наприклад, ті, які надають Open Corporates або інші постачальники URI. Це не для вебсайту організації, його можна надати в полі url в ContactPoint організації.

   Регулярний вираз для цього поля: ``^https?://\S+$``


.. index:: Address, City, Street, Country

.. _Address:

Address
=======

Схема
-----

:streetAddress:
    рядок
     
    |ocdsDescription| Вулиця. Наприклад, вул.Хрещатик, 22.
                                                      
:locality:
    рядок
     
    |ocdsDescription| Населений пункт. Наприклад, Київ.
                                                   
:region:
    рядок
     
    |ocdsDescription| Область. Наприклад, Київська.
                                               
:postalCode:
    рядок
     
    |ocdsDescription| Поштовий індекс, Наприклад, 78043.
                                                    
:countryName:
    рядок, багатомовний, обов’язковий
                                 
    |ocdsDescription| Назва країни. Наприклад, Україна.

:addressDetails:

    Список об’єктів :ref:`Classification`

    Класифікатори адреси, наприклад код територальної громади (КАТОТТГ)


З 01-01-2020 поля countryName та region почнуть перевірятися в усіх нових обʼєктах. Назва країни в полі **countryName** має бути присутня в `довіднику країн <https://prozorroukr.github.io/standards/classifiers/countries.json>`_. Якщо поле countryName заповнене як *Україна* і поле **region** заповнене, його вміст має бути присутнім в `каталозі регіонів України <https://prozorroukr.github.io/standards/classifiers/ua_regions.json>`_. Для існуючих обʼєктів валідація застосовуватися не буде. 


.. index:: Person, Phone, Email, Website, ContactPoint

.. _ContactPoint:

ContactPoint
============

Схема
-----

:name:
    рядок, багатомовний, обов’язковий
                                 
    |ocdsDescription| Ім’я контактної особи, назва відділу чи контактного пункту для листування, що стосується цього процесу укладання договору.
                                                                                                                                            
:email:
    email
     
    |ocdsDescription| Адреса електронної пошти контактної особи/пункту.
                                                                   
:telephone:
    рядок
     
    |ocdsDescription| Номер телефону контактної особи/пункту. Повинен включати міжнародний телефонний код.

    Повинне бути заповнене хоча б одне з полів: або `email`, або `telephone`.
                                                                         
:faxNumber:
    рядок
     
    |ocdsDescription| Номер факсу контактної особи/пункту. Повинен включати міжнародний телефонний код.
                                                                                                   
:url:
    url
   
    |ocdsDescription| Веб адреса контактної особи/пункту.

    Регулярний вираз для цього поля: ``^https?://\S+$``


Додаткові поля для :ref:`base-contracting`, :ref:`openeu` and :ref:`competitivedialogue`:

:availableLanguage:
    рядок

    Можливі значення:

    * `uk` - українська мова
    * `en` - англійська мова
    * `ru` - російська мова

    Визначає мови спілкування.
                          


