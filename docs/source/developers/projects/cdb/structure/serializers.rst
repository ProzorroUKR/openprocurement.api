.. _cdb_context:

Serializers
===========

Класси або функції, які приймають структуру з БД
і повертають форматований/фільтрований об'єкт-відповідь,
який безпосередньо конвертуєтся до json-строки і надсилаєтся в тілі http відповіді.

Серіалізатори також приховують та маскують дані, що визначаєтся бізнес правилами.
Таким чином серіалізатори реалізують бізнес логіку, що не дуже добре.
Краще мати різні серіалізатори, які керуются кодом, що визначає бізнес логіку.

Приклад:

.. sourcecode:: python

    class ChildObjectSerializer(BaseSerializer):
        serializers = {
            "description": lambda x: x if x else "No description",
        }


    class ObjectSerializer(BaseSerializer):
        serializers = {
            "child": ChildObjectSerializer,
        }
