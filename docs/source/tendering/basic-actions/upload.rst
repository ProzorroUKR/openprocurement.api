.. _upload:

Завантаження документів
=======================

Всі точки входу API завантаження документів використовують той самий набір правил.

Завантажити документ з реєстрацією
----------------------------------

#. :ref:`Зареєструвати завантаження документа в Document Service <documentservice:register-document-upload>`.

#. Додати документ в API:

    .. http:example:: ../belowthreshold/http/tutorial/upload-tender-notice.http
        :code:

#. :ref:`Завантажити документ в document service <documentservice:upload-document>`.

Завантажити документ без реєстрації
-----------------------------------

#. :ref:`Зареєструвати завантаження документа в Document Service <documentservice:upload-document-w-o-registration>`.

#. Додати документ в API:

    .. http:example:: ../belowthreshold/http/tutorial/upload-tender-notice.http
        :code:


:ref:`Перейдіть за посиланням, щоб переглянути більше прикладів запитів по документам <bt-documents-tutorial>`.
