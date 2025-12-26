.. _contract-owner:


Встановлення contract owner
===========================

Для подальшого укладання електронного договору (:ref:`econtracting_tutorial`) в закупівлі можна встановити майданчики, з яких буде виконуватися робота з договором (СЕДО).

Для замовника майданчик має бути вказаний в одному з об'єктів разом з `signerInfo`:

* `procuringEntity`
*  `buyers`

Для постачальника майданчик має бути вказаний в об'єкті `bid.tenderers` разом з `signerInfo`.

Поле `contract_owner` може бути встановлене тільки разом з `contractTemplateName` в закупівлі і  `signerInfo` для цього ж об'єкта.

Якщо в об'єкті не вказано `signerInfo` чи нема `contractTemplateName` в закупівлі, ми побачимо помилку:

.. http:example:: ./http/contract-owner/add-contract-owner-no-template.http
   :code:

В полі `contract_owner` дозволено вказувати один з майданчиків, який має 6 рівень акредитації.

В майбутньому контракті тільки ці майданчики будуть мати змогу згенерувати токен і працювати з контрактом в залежності від ролі (`supplier` чи `buyer`).

Якщо майданчик, вказаний як `contract_owner`, не має 6 рівня акреддитації, то ми побачимо помилку:

.. http:example:: ./http/contract-owner/add-contract-owner-invalid-broker.http
   :code:

Успішне додавання `contract_owner` разом з `contractTemplateName` в закупівлі і  `signerInfo` для замовника в `procuringEntity`:

.. http:example:: ./http/contract-owner/add-contract-owner-buyer.http
   :code:

Успішне додавання `contract_owner` разом з `contractTemplateName` в закупівлі і  `signerInfo` для постачальника в `bid.tenderers`:

.. http:example:: ./http/contract-owner/add-contract-owner-supplier.http
   :code:

Після створення контракту ці майданчики можуть згенерувати токен для подальшої роботи з договором.

Подивимося як виглядає договір, в ньому є `contract_owner` в об'єктах `buyer` and `suppliers`:

.. http:example:: ./http/contract-owner/get-contract-owners.http
   :code:
