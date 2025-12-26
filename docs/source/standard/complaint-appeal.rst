
.. include:: defs.hrst

.. index:: ComplaintAppeal, dispute

.. _complaint-appeal:

ComplaintAppeal
===============

Схема
-----

:id:
    uid, генерується автоматично

    Унікальний ідентифікатор апеляції

:description:
    рядок, обов’язковий

    Опис апеляції

:author:
    рядок, генерується автоматично

    Автор, ким було подано інформацію про оскарження скарги в суді

:documents:
    Список об’єктів :ref:`document`

:legislation:
    Список об’єктів :ref:`LegislationItem`. Генерується автоматично.

:proceeding:
    Об'єкт :ref:`complaint-appeal-proceeding`

:dateCreated:
    рядок, :ref:`date`, генерується автоматично

:datePublished:
    рядок, :ref:`date`, генерується автоматично



.. _complaint-appeal-proceeding:

Proceeding
==========

Схема
-----

:dateProceedings:
    рядок, :ref:`date`, обов’язковий

    Дата прийняття до розгляду

:proceedingNumber:
    рядок, обов’язковий

    Номер впровадження
