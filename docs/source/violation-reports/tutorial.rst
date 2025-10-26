.. _violation_reports:

Violation Reports API
=====================


Post a violation report
-----------------------

You create it from a contract. All the documents are posted along with the data.

.. http:example:: http/01-create-violation-report-draft.http
   :code:


It's in `draft` state. You need to add a signature doc before publishing.


.. http:example:: http/02-post-violation-report-draft-signature.http
   :code:

Change status from `draft` to `pending` to publish the report.


.. http:example:: http/03-publish-violation-report-draft.http
   :code:


See `defendantPeriod` and `decisionPeriod` that restrict the periods of the response and decision objects can be posted.


Post the defendant statement
----------------------------

.. http:example:: http/04-create-defendant-statement.http
   :code:


Add an evidence document

.. http:example:: http/05-add-defendant-statement-evidence.http
   :code:


Add a signature document

.. http:example:: http/06-add-defendant-statement-signature.http
   :code:


Post the decision
-----------------

.. http:example:: http/07-create-decision.http
   :code:


Add a signature document

.. http:example:: http/08-post-decision-signature.http
   :code:


See the result violation report object
--------------------------------------

.. http:example:: http/09-get-violation-report.http
   :code:


Field `status` of violation report depends on the decision status now.
