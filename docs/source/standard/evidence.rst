
.. include:: defs.hrst

.. index:: Evidence
.. _evidence:

Evidence
========

Схема
-----

:id:
    uid, генерується автоматично

:title:
    рядок, багатомовний

    |ocdsDescription| Назва доказу.

:description:
    рядок, багатомовний

    |ocdsDescription| Опис доказу.

:type:
    string

    |ocdsDescription| форма, в якій відповідач надає доказ.

    Можливі значення:
     :`document`:
       Документ, що зберігається в системі Prozorro
     :`statement`:
       Машиночитане підтвердження

:relatedDocument:
    :ref:`Reference`

    |ocdsDescription| Id пов'язоного документу з bid/award
