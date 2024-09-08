.. _cdb_views:

Views
=====

Клас з методами або функції,
що викликає WSGI application для обробки http запита клієнта.

Що робить view:

- Працює з БД
- Перевіряє авторизацію (Authorization header)
- Перевіряє формат переданих даних (Models)
- Викликає код бізнес логіки  (State Classes)
- Викликає серіалізатор для формату відповіді (Serializes)

Що НЕ робить view:

- Не реалізує жодної бізнес логіки (Однакові для всіх типів процедур)

Views є таким собі ключовим хабом, який збирає до купи різні компоненти системи.
Розбиратись з якимось фукнціоналом буде краще починаючи з них.

Приклад:

.. sourcecode:: python

    class ObjectResource(BaseResource):
        serializer_class = ObjectSerializer

        @json_view(
            permission="patch_permission",
        )
        def patch(self, uid):
            with database.get_and_update(pk=uid) as obj:
                data = self.model_class(self.request.data).validate()
                self.state_class.on_patch(obj, data)
            logger.info("Object has been updated", extra={"OBJ_ID": uid})
            return {
                "data": self.serializer_class(obj).data,
            }

Predicates
----------

.. admonition:: TODO

   Текст

View validation level
---------------------

.. admonition:: TODO

   Текст

Permissions validators
~~~~~~~~~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Data model validators
~~~~~~~~~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Allowed examples
~~~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Not allowed examples
~~~~~~~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Endpoints
---------

.. admonition:: TODO

   Текст

List endpoints
~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Get endpoints
~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Post endpoints
~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст

Patch endpoints
~~~~~~~~~~~~~~

.. admonition:: TODO

   Текст