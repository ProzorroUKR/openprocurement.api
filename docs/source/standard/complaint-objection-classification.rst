
.. include:: defs.hrst

.. index:: ComplaintObjectionClassification, dispute

.. _complaint-objection-classification:

ComplaintObjectionClassification
================================

Schema
------

:scheme:
    string, required

    Scheme of the classification of the essence of the objection.
    Possible values are:

    * `article_16`
    * `article_17`
    * `other`
    * `violation_amcu`
    * `amcu`
    * `amcu_24`

:id:
    string, required

    Id of the classification of the essence of the objection.
    Should be from particular standards dictionary due to scheme.

:description:
    string, required

    Description of the classification of the essence of the objection
