.. _stand-still-to-pre-qualification:

Repeat of the preliminary qualification
=======================================

There are two ways to return a tender to the preliminary qualification stage:

1. Patching the tender status from active.pre-qualification.stand-still to active.pre-qualification.
2. Resolve the complaint.

Before proceeding to the description of the steps, let’s ensure that the tender is in the active.pre-qualification.stand-still status:

.. http:example:: http/back-to-pre-qualification/tender-pre-qualification-stand-still.http
   :code:


1-st Way: Update Tender Status
------------------------------

If you want to return to the preliminary qualification stage by updating the tender status through a PATCH request,
you must ensure that there are no complaints with the statuses `draft`, `pending`, or `accepted` on the qualification object.

For example you have two complaints in `draft` and `pending` statuses:

.. http:example:: http/back-to-pre-qualification/complaint-list-1.http
   :code:

If you try to patch tender to `active.pre-qualification.stand-still` status, you'll get error:

.. http:example:: http/back-to-pre-qualification/switch-tender-to-pre-qualification-forbid.http
   :code:

After changing 1-st to complaint to `mistaken` status and 2-nd status:

.. http:example:: http/back-to-pre-qualification/complaint-list-2.http
   :code:

You can successfully return to previous stage:

.. http:example:: http/back-to-pre-qualification/switch-tender-to-pre-qualification-success.http
   :code:


2-nd Way: Resolve Complaint
---------------------------

You can resolve existing complaint(complaint resolving process you can see in :ref:`qualification-complaint-resolution`):

.. http:example:: http/back-to-pre-qualification/qualification-complaint-satisfy.http
   :code:

And system automatically switch tender to preliminary qualification stage:

.. http:example:: http/back-to-pre-qualification/check-tender-pre-qualification.http
   :code:
