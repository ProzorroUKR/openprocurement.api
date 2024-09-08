.. _cdb_models:

Models
======

Код який валідує структуру та формат переданих даних.

Приклад:

.. sourcecode:: python

    class ChildObject(BaseModel):
        title = StringType(required=True)
        description = StringType()


    class Object(BaseModel):
        id = MD5Type(required=True)
        child = ModelType(ChildObject, required=True)

Треба бути уважним, бо деякі перевірки даних насправді краще робити в StateClasses.

Приклади, що описує/валідує Models

- Структуру даних
- Формат, тип полів
- Обов'яковість полів, якщо вона не залежить від бізнес процесів


Приклади, що  НЕ описує/валідує Models

- Зміна даних в об'єкті з одних на інші

Model Types
-----------

.. admonition:: TODO

   Текст

Post Model
~~~~~~~~~~

.. admonition:: TODO

   Текст

Patch Model
~~~~~~~~~~

.. admonition:: TODO

   Текст

General Model
~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Model validation level
---------------------

.. admonition:: TODO

   Текст

Allowed examples
~~~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Not allowed examples
~~~~~~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст
