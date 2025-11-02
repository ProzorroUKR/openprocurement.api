.. _violation_reports_tutorial:

Violation Reports Tutorial
==========================


Post a violation report
-----------------------

You create it from a contract. All the documents are posted along with the data

.. http:example:: http/01-00-post-report-draft.http
   :code:

While in `draft` state, it can be changed

.. http:example:: http/01-01-patch-report-draft.http
   :code:


You can delete a document

.. http:example:: http/01-02-delete-document.http
   :code:


Then post a new one

.. http:example:: http/01-03-post-details-document.http
   :code:


Or you can update document version with PUT method

.. http:example:: http/01-04-put-report-document-evidence.http
   :code:

Update document details can be changed using PATCH method

.. http:example:: http/01-05-patch-report-document-evidence.http
   :code:


Before publishing, it's required to add a signature document

.. http:example:: http/01-06-post-report-draft-signature.http
   :code:


Now you can publish your violation report by changing its status

.. http:example:: http/01-07-publish-report-draft.http
   :code:


See `defendantPeriod` that restrict the periods of the response can be posted.
The decision can be posted once the period ends.


Post the defendant statement
----------------------------
Post a `draft` dependant statement

.. http:example:: http/02-01-put-defendant-statement.http
   :code:


While is not active, you can update it

.. http:example:: http/02-02-update-defendant-statement.http
   :code:

You can delete a document

.. http:example:: http/02-03-delete-document.http
   :code:


Then post a new one

.. http:example:: http/02-04-post-defendant-document.http
   :code:


And update the evidences

.. http:example:: http/02-05-put-defendant-statement-evidence.http
   :code:


Change documents descriptions

.. http:example:: http/02-06-patch-defendant-statement-evidence.http
   :code:


Before publishing it's required to add a signature document


.. http:example:: http/02-07-post-defendant-statement-signature.http
   :code:


Then publish the statement, so it appears in the feed

.. http:example:: http/02-08-publish-defendant-statement.http
   :code:


Post the decision
-----------------

Create a `draft` decision

.. http:example:: http/03-01-create-decision.http
   :code:


It's required to add a signature document

.. http:example:: http/03-02-post-decision-signature.http
   :code:


While in `draft`, you can change the decision


.. http:example:: http/03-03-change-decision.http
   :code:


You can delete a document

.. http:example:: http/03-04-delete-document.http
   :code:


Then post a new one

.. http:example:: http/03-05-post-decision-document.http
   :code:


Before publishing, you need to update the signature

.. http:example:: http/03-06-put-decision-signature.http
   :code:


Publish the decision

.. http:example:: http/03-07-publish-decision.http
   :code:


See the result violation report object
--------------------------------------

.. http:example:: http/04-01-get-violation-report.http
   :code:


Field `status` of violation report depends on the decision status now.


Feed violation report updates
-----------------------------

Violation reports appear in their feed when the get public changes.

These are:
  1. violationReport is published
  2. defendantStatement is published
  3. decision is published


.. http:example:: http/05-01-feed.http
   :code:


Process objects in `data` and follow the `next_page`

.. http:example:: http/05-02-feed-empty.http
   :code:

Once `data` is empty make your script sleep for a while and check the same page later.
