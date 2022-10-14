Example for Tender
------------------

Tender ownership change
~~~~~~~~~~~~~~~~~~~~~~~

Let's view transfer example for tender.


Tender creation
^^^^^^^^^^^^^^^

At first let's create a tender:

.. http:example:: tutorial/create-tender.http
   :code:

`broker` is current tender's ``owner``.

Note that response's `access` section contains a ``transfer`` key which is used to change tender ownership. 

After tender's registration in CDB broker has to provide its customer with ``transfer`` key.

Transfer creation
^^^^^^^^^^^^^^^^^

Broker that is going to become new tender owner should create a `Transfer`.

.. http:example:: tutorial/create-tender-transfer.http
   :code:

`Transfer` object contains new access ``token`` and new ``transfer`` token for the object that will be transferred to new broker.

`Transfer` can be retrieved by `id`:

.. http:example:: tutorial/get-tender-transfer.http
   :code:

Changing tender's owner
^^^^^^^^^^^^^^^^^^^^^^^

An ability to change tender's ownership depends on tender's status:

+--------------------------------------+-----------------------+
|                Allowed               |      Not Alowwed      |
+--------------------------------------+-----------------------+
|                      **belowThreshold**                      |
+--------------------------------------+-----------------------+
| active.enquiries                     | complete              |
|                                      |                       |
| active.tendering                     | cancelled             |
|                                      |                       |
| active.auction                       | unsuccessful          |
|                                      |                       |
| active.qualification                 |                       |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|                     **aboveThresholdUA**                     |
+--------------------------------------+-----------------------+
| active.tendering                     | complete              |
|                                      |                       |
| active.auction                       | cancelled             |
|                                      |                       |
| active.qualification                 | unsuccessful          |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|                     **aboveThresholdEU**                     |
+--------------------------------------+-----------------------+
| active.tendering                     | complete              |
|                                      |                       |
| active.pre-qualification             | cancelled             |
|                                      |                       |
| active.pre-qualification.stand-still | unsuccessful          |
|                                      |                       |
| active.auction                       |                       |
|                                      |                       |
| active.qualification                 |                       |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|                 **aboveThresholdUA.defense**                 |
+--------------------------------------+-----------------------+
| active.tendering                     | complete              |
|                                      |                       |
| active.auction                       | cancelled             |
|                                      |                       |
| active.qualification                 | unsuccessful          |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|                   **competitiveDialogueUA**                  |
+--------------------------------------+-----------------------+
| active.tendering                     | active.stage2.waiting |
|                                      |                       |
| active.pre-qualification             | complete              |
|                                      |                       |
| active.pre-qualification.stand-still | unsuccessful          |
|                                      |                       |
| active.stage2.pending                | cancelled             |
+--------------------------------------+-----------------------+
|               **competitiveDialogueUA.stage2**               |
+--------------------------------------+-----------------------+
| draft.stage2                         | complete              |
|                                      |                       |
| active.tendering                     | unsuccessful          |
|                                      |                       |
| active.auction                       | cancelled             |
|                                      |                       |
| active.qualification                 |                       |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|                   **competitiveDialogueEU**                  |
+--------------------------------------+-----------------------+
| active.tendering                     | active.stage2.waiting |
|                                      |                       |
| active.pre-qualification             | complete              |
|                                      |                       |
| active.pre-qualification.stand-still | unsuccessful          |
|                                      |                       |
| active.stage2.pending                | cancelled             |
+--------------------------------------+-----------------------+
|               **competitiveDialogueEU.stage2**               |
+--------------------------------------+-----------------------+
| draft.stage2                         | complete              |
|                                      |                       |
| active.tendering                     | unsuccessful          |
|                                      |                       |
| active.pre-qualification             | cancelled             |
|                                      |                       |
| active.pre-qualification.stand-still |                       |
|                                      |                       |
| active.auction                       |                       |
|                                      |                       |
| active.qualification                 |                       |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|                           **esco**                           |
+--------------------------------------+-----------------------+
| active.tendering                     | complete              |
|                                      |                       |
| active.pre-qualification             | unsuccessful          |
|                                      |                       |
| active.pre-qualification.stand-still | cancelled             |
|                                      |                       |
| active.auction                       |                       |
|                                      |                       |
| active.qualification                 |                       |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|                 **closeFrameworkAgreementUA**                |
+--------------------------------------+-----------------------+
| active.tendering                     | complete              |
|                                      |                       |
| active.pre-qualification             | unsuccessful          |
|                                      |                       |
| active.pre-qualification.stand-still | cancelled             |
|                                      |                       |
| active.auction                       |                       |
|                                      |                       |
| active.qualification                 |                       |
|                                      |                       |
| active.qualification.stand-still     |                       |
|                                      |                       |
| active.awarded                       |                       |
+--------------------------------------+-----------------------+
|            **closeFrameworkAgreementSelectionUA**            |
+--------------------------------------+-----------------------+
| draftactive.enquiries                | draft.pending         |
|                                      |                       |
| active.tendering                     | draft.unsuccessful    |
|                                      |                       |
| active.auction                       | complete              |
|                                      |                       |
| active.qualification                 | unsuccessful          |
|                                      |                       |
| active.awarded                       | cancelled             |
+--------------------------------------+-----------------------+
|                         **reporting**                        |
+--------------------------------------+-----------------------+
| active                               | complete              |
|                                      |                       |
|                                      | cancelled             |
+--------------------------------------+-----------------------+
|                        **negotiation**                       |
+--------------------------------------+-----------------------+
| active                               | complete              |
|                                      |                       |
|                                      | cancelled             |
+--------------------------------------+-----------------------+
|                     **negotiation.quick**                    |
+--------------------------------------+-----------------------+
| active                               | complete              |
+--------------------------------------+-----------------------+

To change tender's ownership new broker should send POST request to appropriate `/tenders/id/` with `data` section containing ``id`` of `Transfer` and ``transfer`` token received from customer:

.. http:example:: tutorial/change-tender-ownership.http
   :code:

Updated ``owner`` value indicates that ownership is successfully changed. 

Note that new broker has to provide its customer with new ``transfer`` key (generated in `Transfer` object).

After `Transfer` is applied it stores tender path in ``usedFor`` property:

.. http:example:: tutorial/get-used-tender-transfer.http
   :code:

'Used' `Transfer` can't be applied to any other object.

Let's try to change the tender using ``token`` received on `Transfer` creation:

.. http:example:: tutorial/modify-tender.http
   :code:

Pay attention that only broker with appropriate accreditation level can become new owner. Otherwise broker will be forbidden from this action.

.. http:example:: tutorial/change-tender-ownership-forbidden.http
   :code:

Also ownership change is allowed only if current owner has a special accreditation level that allows ownership change:

.. http:example:: tutorial/change-tender-ownership-forbidden-owner.http
   :code:
