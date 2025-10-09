.. _violation_reports:

Violation Reports API
=====================


Post a violation report
-----------------------

You create it from a contract. All the documents are posted along with the data.

.. http:example:: http/create-violation-report.http
   :code:


Field `status` of violation report is "pending".
See `defendantPeriod` and `decisionPeriod` that restrict the periods of the response and decision objects can be posted.


Post the defendant statement
----------------------------

.. http:example:: http/create-defendant-statement.http
   :code:


Post the decision
-----------------

.. http:example:: http/create-decision.http
   :code:


See the result violation report object
--------------------------------------

.. http:example:: http/get-violation-report.http
   :code:


Field `status` of violation report depends on the decision status now.
