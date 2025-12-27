.. _upload:

Завантаження документів
=======================

Всі точки входу API завантаження документів використовують той самий набір правил.

Завантажити документ з реєстрацією
----------------------------------

1. :ref:`Зареєструвати завантаження документа в Document Service <documentservice:register-document-upload>`.

2. Додати документ в API:

.. http:example:: ../belowthreshold/http/tutorial/upload-tender-notice.http
    :code:

3. :ref:`Завантажити документ в document service <documentservice:upload-document>`.

Завантажити документ без реєстрації
-----------------------------------

1. :ref:`Зареєструвати завантаження документа в Document Service <documentservice:upload-document-w-o-registration>`.

2. Додати документ в API:

.. http:example:: ../belowthreshold/http/tutorial/upload-tender-notice.http
    :code:


:ref:`Перейдіть за посиланням, щоб переглянути більше прикладів запитів по документам <bt-documents-tutorial>`.
