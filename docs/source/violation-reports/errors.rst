.. _violation_reports_errors:

Violation Reports API Errors
============================


DefendantStatement and Decision in `draft` status
--------------------------------------------------

If a violation report is in `draft` status, it's is not public yet.

.. http:example:: http/errors/01-00-get-report.http
   :code:

Posting a defendant statement should fail.

.. http:example:: http/errors/01-01-put-defendant-statement.http
   :code:


Posting a defendant statement document should fail as well.

.. http:example:: http/errors/01-01-put-defendant-statement.http
   :code:


Posting a decision should fail.

.. http:example:: http/errors/01-03-put-decision.http
   :code:


Posting a decision document should also fail.

.. http:example:: http/errors/01-04-post-decision-document.http
   :code:


Violation report in `draft` status
----------------------------------


Patching violation report with extra fields should fail.

.. http:example:: http/errors/01-05-patch-report-extra.http
   :code:


Patching violation report with no changes should succeed while dateModified should be the same.

.. http:example:: http/errors/01-06-patch-report-no-changes.http
   :code:
