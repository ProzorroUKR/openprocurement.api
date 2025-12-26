
.. include:: defs.hrst

.. index:: ComplaintObjection, dispute

.. _complaint-objection:

ComplaintObjection
==================

Схема
-----

:id:
    uid, генерується автоматично

    Унікальний ідентифікатор заперечення

:title:
    рядок, обов’язковий

    Назва заперечення

:description:
    string

    Опис заперечення

:relatesTo:
    рядок, обов’язковий

    Тип пов'яазного елемента. Можливі значення:

    * `tender`
    * `lot`
    * `award`
    * `qualification`
    * `cancellation`

:relatedItem:
    рядок, обов’язковий

    Ідентифікатор пов'яазного елемента.

:classification:
    :ref:`complaint-objection-classification`

:requestedRemedies:
    Список об’єктів :ref:`complaint-objection-requested-remedy`

:arguments:
    Список об’єктів :ref:`complaint-objection-argument`

:sequenceNumber:
    integer, non negative

