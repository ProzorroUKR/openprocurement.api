Example for Plan
------------------

Plan ownership change
~~~~~~~~~~~~~~~~~~~~~~~

Let's view transfer example for plan.


Tender creation
^^^^^^^^^^^^^^^

At first let's create a plan:

.. http:example:: tutorial/create-plan.http
   :code:

`broker` is current plan's ``owner``.

Note that response's `access` section contains a ``transfer`` key which is used to change plan ownership.

After plan's registration in CDB broker has to provide its customer with ``transfer`` key.

Transfer creation
^^^^^^^^^^^^^^^^^

Broker that is going to become new plan owner should create a `Transfer`.

.. http:example:: tutorial/create-plan-transfer.http
   :code:

`Transfer` object contains new access ``token`` and new ``transfer`` token for the object that will be transferred to new broker.

`Transfer` can be retrieved by `id`:

.. http:example:: tutorial/get-plan-transfer.http
   :code:

Changing plan's owner
^^^^^^^^^^^^^^^^^^^^^^^

An ability to change plan's ownership depends on plan's status:

+-----------+-------------+
| Allowed   | Not Allowed |
+-----------+-------------+
| scheduled | draft       |
|           |             |
|           | cancelled   |
|           |             |
|           | complete    |
+-----------+-------------+

To change plan's ownership new broker should send POST request to appropriate `/plans/id/` with `data` section containing ``id`` of `Transfer` and ``transfer`` token received from customer:

.. http:example:: tutorial/change-plan-ownership.http
   :code:

Updated ``owner`` value indicates that ownership is successfully changed. 

Note that new broker has to provide its customer with new ``transfer`` key (generated in `Transfer` object).

After `Transfer` is applied it stores plan path in ``usedFor`` property:

.. http:example:: tutorial/get-used-plan-transfer.http
   :code:

'Used' `Transfer` can't be applied to any other object.

Let's try to change the plan using ``token`` received on `Transfer` creation:

.. http:example:: tutorial/modify-plan.http
   :code:

Pay attention that only broker with appropriate accreditation level can become new owner. Otherwise broker will be forbidden from this action.

.. http:example:: tutorial/change-plan-ownership-forbidden.http
   :code:

Also ownership change is allowed only if current owner has a special accreditation level that allows ownership change:

.. http:example:: tutorial/change-plan-ownership-forbidden-owner.http
   :code:
