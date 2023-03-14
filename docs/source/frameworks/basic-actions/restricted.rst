Restricted access
=================

Framework can have restricted access with next rules

+---------------+------------+--------------------------------+------------------------+
| Object        | Public API | Private API (Procuring Entity) | Private API (Supplier) |
+===============+============+================================+========================+
| framework     | view       | view/edit                      | view                   |
+---------------+------------+--------------------------------+------------------------+
| submission    | –          | view (all)                     | view/edit (own)        |
+---------------+------------+--------------------------------+------------------------+
| qualification | –          | view/edit (all)                | view (own)             |
+---------------+------------+--------------------------------+------------------------+
| agreement     | –          | view/edit (all)                | –                      |
+---------------+------------+--------------------------------+------------------------+

Let's make an agreement that `Procuring Entity` and `Suppliers` will use different brokers for working with API:

- Procuring Entity uses `Broker`
- Supplier 1 uses `Broker 1`
- Supplier 2 uses `Broker 2`

Create Framework with restricted access
---------------------------------------

First create framework with restricted access by `Broker`.
To do this, we need to set ``restricted_derivatives`` field to ``true`` in ``config`` section of framework creation request.

.. http:example:: http/restricted/framework-create-broker.http
   :code:

This framework by itself is visible to everyone in public API.

.. note::
    For `ProcuringEntity` with `defense` kind ``restricted_derivatives`` field will be set to ``true`` automatically.

The second step is moving the framework to `active` status:

.. http:example:: http/restricted/framework-activate-broker.http
   :code:

Create and activate Submissions with restricted access
------------------------------------------------------

After activating framework, users can register their submissions in period from `framework.enquiryPeriod.endDate` to `period.Date`.

Let's register submission by `Broker 1`:

.. http:example:: http/restricted/submission-register-broker1.http
   :code:

You can see that ``restricted`` field was set to ``true`` in ``config`` section of submission creation response.

Next activate submission by `Broker 1`:

.. http:example:: http/restricted/submission-activate-broker1.http
   :code:

Add another Submission by `Broker 2`:

.. http:example:: http/restricted/submission-register-broker2.http
   :code:

And activate it:

.. http:example:: http/restricted/submission-activate-broker2.http
   :code:

Request submissions with restricted access
------------------------------------------

Let's check submissions by all participants:

Broker (Procuring Entity)
***************************

Let's check submission feed for `Broker` that is `Procuring Entity` and has access to all submissions of framework:

.. http:example:: http/restricted/submission-feed-broker.http
   :code:

Now make request by `Broker` for submission that was created by `Broker 1`:

.. http:example:: http/restricted/submission-get-1-broker.http
   :code:

Then make request by `Broker` for submission that was created by `Broker 2`:

.. http:example:: http/restricted/submission-get-2-broker.http
   :code:

Broker 1 (Supplier 1)
*********************

Let's check submission feed for `Broker 1` that is `Supplier 1` and has access only to own submissions:

.. http:example:: http/restricted/submission-feed-broker1.http
   :code:

We can see that second submission is partially visible in feed and marked with ``restricted`` field set to ``true``.

Now make request by `Broker 1` for submission that was created by `Broker 1`:

.. http:example:: http/restricted/submission-get-1-broker1.http
   :code:

Then make request by `Broker 1` for submission that was created by `Broker 2`:

.. http:example:: http/restricted/submission-get-2-broker1.http
   :code:

We can see error message that submission is restricted for `Broker 1`.

Broker 2 (Supplier 2)
*********************

Let's check submission feed for `Broker 2` that is `Supplier 2` and has access only to own submissions:

.. http:example:: http/restricted/submission-feed-broker1.http
   :code:

Now make request by `Broker 2` for submission that was created by `Broker 1`:

.. http:example:: http/restricted/submission-get-1-broker2.http
   :code:

Then make request by `Broker 2` for submission that was created by `Broker 2`:

.. http:example:: http/restricted/submission-get-2-broker2.http
   :code:

Anonymous
*********

Let's check submission feed with anonymous request (or any broker that is not `Broker` or `Broker 1`):

.. http:example:: http/restricted/submission-feed-anonymous.http
   :code:

Now make request for submission that was created by `Broker 1`:

.. http:example:: http/restricted/submission-get-1-anonymous.http
   :code:

Then make request for submission that was created by `Broker 2`:

.. http:example:: http/restricted/submission-get-2-anonymous.http
   :code:

Request Qualifications with restricted access
---------------------------------------------

Let's check qualifications by all participants:

Broker (Procuring Entity)
***************************

Let's check qualification feed for `Broker` that is `Procuring Entity` and has access to all qualifications of framework:

.. http:example:: http/restricted/submission-feed-broker.http
   :code:

Now make request by `Broker` for qualification of submission that was created by `Broker 1`:

.. http:example:: http/restricted/qualification-get-1-broker.http
   :code:

Then make request by `Broker` for qualification of submission that was created by `Broker 2`:

.. http:example:: http/restricted/qualification-get-2-broker.http
   :code:

Broker 1 (Supplier 1)
*********************

Let's check qualification feed for `Broker 1` that is `Supplier 1` and has access only to qualifications of it own submissions:

.. http:example:: http/restricted/qualification-feed-broker1.http
   :code:

We can see that second qualification is partially visible in feed and marked with ``restricted`` field set to ``true``.

Now make request by `Broker 1` for qualification of submission that was created by `Broker 1`:

.. http:example:: http/restricted/qualification-get-1-broker1.http
   :code:

Then make request by `Broker 1` for qualification of submission that was created by `Broker 2`:

.. http:example:: http/restricted/qualification-get-2-broker1.http
   :code:

We can see error message that qualification is restricted for `Broker 1`.

Broker 2 (Supplier 2)
*********************

Let's check qualification feed for `Broker 2` that is `Supplier 2` and has access only to qualifications of it own submissions:

.. http:example:: http/restricted/qualification-feed-broker1.http
   :code:

Now make request by `Broker 2` for qualification of submission that was created by `Broker 1`:

.. http:example:: http/restricted/qualification-get-1-broker2.http
   :code:

Then make request by `Broker 2` for qualification of submission that was created by `Broker 2`:

.. http:example:: http/restricted/qualification-get-2-broker2.http
   :code:

Anonymous
*********

Let's check qualification feed with anonymous request (or any broker that is not `Broker` or `Broker 1`):

.. http:example:: http/restricted/qualification-feed-anonymous.http
   :code:

Now make request for qualification of submission that was created by `Broker 1`:

.. http:example:: http/restricted/qualification-get-1-anonymous.http
   :code:

Then make request for qualification of submission that was created by `Broker 2`:

.. http:example:: http/restricted/qualification-get-2-anonymous.http
   :code:

Activate Qualifications with restricted access
----------------------------------------------

Let's activate all qualifications by `Broker`:

.. http:example:: http/restricted/qualification-activate-1-broker.http
   :code:

.. http:example:: http/restricted/qualification-activate-2-broker.http
   :code:

Let's check current framework

.. http:example:: http/restricted/framework-with-agreement.http
   :code:

You can see that `agreementID` appeared in current framework, so let's check that agreement.

Request Agreement with restricted access
---------------------------------------------

Let's check agreement by all participants:

Broker (Procuring Entity)
***************************

Let's check agreement feed for `Broker` that is `Procuring Entity` and has access to agreement of framework:

.. http:example:: http/restricted/agreement-feed-broker.http
   :code:

Now make request by `Broker` for agreement:

.. http:example:: http/restricted/agreement-get-broker.http
   :code:


Broker 1 (Supplier 1)
*********************

Let's check agreement feed for `Broker 1`:

.. http:example:: http/restricted/agreement-feed-broker1.http
   :code:

Now make request by `Broker 1` for agreement:

.. http:example:: http/restricted/agreement-get-broker1.http
   :code:

Broker 2 (Supplier 2)
*********************

Let's check agreement feed for `Broker 2`:

.. http:example:: http/restricted/agreement-feed-broker2.http
   :code:

Now make request by `Broker 2` for agreement:

.. http:example:: http/restricted/agreement-get-broker2.http
   :code:


Anonymous
*********

Let's check agreement feed with anonymous request (or any broker that is not `Broker` or `Broker 1`):

.. http:example:: http/restricted/agreement-feed-anonymous.http
   :code:

Now make request for agreement:

.. http:example:: http/restricted/agreement-get-anonymous.http
   :code:
