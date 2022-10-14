Example for Contract
--------------------

Contract ownership change
~~~~~~~~~~~~~~~~~~~~~~~~~

Let's view transfer example for contract transfer.


Getting contract's credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At first let's get contract credentials:

.. httpexample:: tutorial/get-contract-credentials.http
   :code:

`broker` is current contract's ``owner``.

Note that response's `access` section contains a ``transfer`` key which is used to change tender ownership.

After contract's credentials obtaining broker has to provide its customer with ``transfer`` key.

Transfer creation
^^^^^^^^^^^^^^^^^

First of all, you must know ID of the contract that you want to transfer.

Broker that is going to become new contract owner should create a `Transfer`.

.. httpexample:: tutorial/create-contract-transfer.http
   :code:

`Transfer` object contains new access ``token`` and new ``transfer`` token for the object that will be transferred to new broker.

Changing contract's owner
^^^^^^^^^^^^^^^^^^^^^^^^^

An ability to change contract's ownership depends on contract's status:

+---------+-------------+
| Allowed | Not Allowed |
+---------+-------------+
| active  | pending     |
|         |             |
|         | terminated  |
|         |             |
|         | cancelled   |
+---------+-------------+

In order to change contract's ownership new broker should send POST request to appropriate `/contracts/id/` with `data` section containing ``id`` of `Transfer` and ``transfer`` token received from customer:

.. httpexample:: tutorial/change-contract-ownership.http
   :code:

Updated ``owner`` value indicates that ownership is successfully changed. 

Note that new broker has to provide its customer with new ``transfer`` key (generated in `Transfer` object).

After `Transfer` is applied it stores contract path in ``usedFor`` property.

.. httpexample:: tutorial/get-used-contract-transfer.http
   :code:

Let's try to change the contract using ``token`` received on `Transfer` creation:

.. httpexample:: tutorial/modify-contract.http
   :code:

Pay attention that only broker with appropriate accreditation level can become new owner. Otherwise broker will be forbidden from this action.

.. httpexample:: tutorial/change-contract-ownership-forbidden.http
   :code:

Also ownership change is allowed only if current owner has a special accreditation level that allows ownership change:

.. httpexample:: tutorial/change-contract-ownership-forbidden-owner.http
   :code:
