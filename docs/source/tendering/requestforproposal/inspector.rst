.. _requestforproposal_inspector_tutorial:


Tender Inspector Tutorial
=========================


.. index:: Inspector

Creating tender with inspector
------------------------------

To create tender with inspector you should set field `inspector` on creation
(or you can in set it later by patching tender in `draft` or `active.enquiries` statuses)

Inspector field can be set only together with `funders` .

that's what will happen if you try to create tender with inspector without funders:

.. http:example:: http/tutorial/tender-with-inspector-post-without-funders.http
   :code:

We got error 422, now let's create tender with `inspector` together with `funders`:

.. http:example:: http/tutorial/tender-with-inspector-post-success.http
   :code:


Patch inspector
---------------

Field inspector can be patched only in statuses `draft` or `active.enquiries`:

.. http:example:: http/tutorial/patch-tender-inspector-success.http
   :code:


Create review request
---------------------

Review request can create tender owner for tender with inspector and only in `active.enquiries`, `active.qualification` (if procedure with multiple lots)/ `active.awarded` (if procedure with one or without lots).

.. http:example:: http/tutorial/post-tender-review-request-success.http
   :code:

Depends on status from the moment of creation to the moment of providing the result prohibited:
    - `active.enquiries` - PATCH tender(except `tenderPeriod`)
    - `active.qualification`/`active.awarded` - PATCH awards, activate contracts


Let's try to patch tender description:

.. http:example:: http/tutorial/patch-tender-with-unanswered-review-request.http
   :code:

Now let's patch tenderPeriod:

.. http:example:: http/tutorial/patch-tender-period-with-review-request.http
   :code:

New review request can't be created if already exists unanswered review request:

.. http:example:: http/tutorial/post-tender-review-request-already-exist.http
   :code:


Create review request on qualification stage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If procedure has lots, review request should be created with lotID:

.. http:example:: http/tutorial/post-review-request-without-lot-id.http
   :code:

Review request on qualification stage(`active.qualification`/`active.awarded`) can be created only if exists active award.

.. http:example:: http/tutorial/post-review-request-without-active-award.http
   :code:



Inspector providing review result
---------------------------------

Provide result on review request can only user with `inspector` role using PATCH method:

.. http:example:: http/tutorial/patch-tender-review-request-false.http
   :code:

Inspector can't provide review result on the same review request twice:

.. http:example:: http/tutorial/second-patch-tender-review-request-false.http
   :code:

The procedure cannot go further through the statuses until the controller gives a positive response to review request.

So buyer should make changes, create new review request and after that inspector can provide new result:

.. http:example:: http/tutorial/patch-tender-review-request-true.http
   :code: