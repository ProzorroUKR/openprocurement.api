

.. index:: Question, Answer, Author
.. _question:

Question
========

Схема
-----

:id:
    uid, генерується автоматично

:author:
    :ref:`Organization`, обов’язково

    Хто подає звернення (contactPoint - людина, identification - організація, яку ця людина представляє).

:title:
    рядок, обов’язковий

    Назва звернення.

:description:
    рядок

    Опис звернення.

:date:
    рядок, :ref:`date`, генерується автоматично

    Дата публікації.

:dateAnswered:
    рядок, :ref:`date`, генерується автоматично

    Дата, коли було надано відповідь.

:answer:
    рядок

    Відповідь на звернення.

:questionOf:
    рядок

    Можливі значення:

    * `tender`
    * `item`
    * `lot`

:relatedItem:
    рядок

    ID пов’язаних :ref:`lot` або :ref:`item`.
