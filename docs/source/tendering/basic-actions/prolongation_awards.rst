.. _prolongation-awards:

Подовження строку розгляду award
================================

Для всіх процедур, окрім :ref:`limited` та :ref:`belowThreshold`, існує можливість подовжити строк розгляду аварду.

Під час створення ававрду, з'являється поле `period`. По замовчуванню є 5 робочих днів на прийняття рішення:

.. http:example:: ./http/prolongation-awards/award-get.http
   :code:

.. note::
    Поле `period` буде відсутнє в авардах :ref:`limited`.

Для того, щоб подовжити строк розгляду аварду до 20 робочих днів, замовник має додати майлстоун з кодом `extensionPeriod`:

.. http:example:: ./http/prolongation-awards/award-milestone-extension-post.http
   :code:

Тільки один майлстоун з типом `extensionPeriod` може бути доданий до аварду:

.. http:example:: ./http/prolongation-awards/award-milestone-extension-invalid-post.http
   :code:

Після цього необхідно загрузити документ з `documentType: extensionReport`:

.. http:example:: ./http/prolongation-awards/award-extension-report-post.http
   :code:

Тільки один документ з типом `extensionReport` може бути доданий до аварду:

.. http:example:: ./http/prolongation-awards/award-extension-report-invalid-post.http
   :code:

Тепер подивимося на авард, в ньому змінилося поле `period.endDate` з 5 робочих днів до 20 робочих днів від дати початку розгляду:

.. http:example:: ./http/prolongation-awards/award-extension-get.http
   :code:

.. note::
     Для :ref:`pricequotation` є 2 робочі дні на прийняття рішення та можна подовжити строк розгляду аварду до 5 робочих днів з майлстоуном `extensionPeriod`.
