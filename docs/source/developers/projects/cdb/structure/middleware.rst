.. _cdb_middlewares:

Middlewares
===========
Код який виконуєтся для кожного запиту до сервіса на початку і наприкінці обробки запита,
тобто до view і після.

Що робить middleware:

- Загальні речі які робить кожен запит вашого застосунку (зберігає в контекст якісь куки, шось логує, шось рахує)

Що НЕ робить middleware:

- Ніякої бізнес логіки або чогось специфічого тільки для частини views

.. admonition:: TODO

   Приклад
