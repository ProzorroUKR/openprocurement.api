
.. include:: defs.hrst

.. index:: EContractCancellation
.. _econtractcancellation:

EContractCancellation
=====================

Схема
-----

:id:
    uid, генерується автоматично

:reason:
    рядок, обов'язковий

    Причина, з якої скасовується об'єкт.

:reasonType:
    рядок

    Можливі значення:

    * `requiresChanges`
    * `signingRefusal`

:status:
    рядок

    Можливі значення:
     :`pending`:
       Запит оформлюється.
     :`active`:
       Скасування активоване.

:dateCreated:
    рядок, генерується автоматично, :ref:`date`

    Дата створення скасування.

:author:
    рядок, генерується автоматично

    Автор скасування

