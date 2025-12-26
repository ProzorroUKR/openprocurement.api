
.. _complaint-payments:


Оплати по скаргах
=================


Cтворимо скаргу:

.. http:example:: ./http/complaints-value/complaint-creation.http
   :code:


Ви можете побачити поле `value`, яке містить суму, яку потрібно сплатити за цю скаргу


Якщо валюта тендеру відрізняється від UAH, то при розміщені скарги, буде надіслано запит на bank.gov.ua для розрахування значення `value` у гривні. Це також може спричинити помилки підключення різних типів:

.. http:example:: ./http/complaints-value/complaint-creation-decoding.http
   :code:

.. http:example:: ./http/complaints-value/complaint-creation-connection.http
   :code:

У випадку коду 409 запит слід повторити. Але не треба у випадку 422:

.. http:example:: ./http/complaints-value/complaint-creation-rur.http
   :code:

