
.. include:: defs.hrst

.. index:: ComplaintPost, dispute

.. _complaintpost:

ComplaintPost
=============

Схема
-----

:title:
   рядок, обов’язковий

:description:
   рядок, обов’язковий

:relatedPost:
    рядок

    Ідентифікатор пов’язаного :ref:`complaintpost`-а.

:recipient:
    рядок, обов’язковий

    Можливі значення:

    * `complaint_owner`
    * `tender_owner`
    * `aboveThresholdReviewers`

:author:
    рядок, генерується автоматично

    Можливі значення:

    * `complaint_owner`
    * `tender_owner`
    * `aboveThresholdReviewers`

:datePublished:
   рядок, :ref:`date`, генерується автоматично
