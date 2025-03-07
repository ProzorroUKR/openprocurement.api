.. _documents-deletion:

Documents Deletion
===================

There is a possibility to delete documents in `draft` objects such as plan, tender, bid.

Delete document tutorial
---------------------------

For deletion document in tender we should use an API endpoint with particular document id from tender:

.. http:example:: ../belowthreshold/http/tutorial/delete-tender-doc.http
    :code:

Let's try to delete document in not `draft` tender and we will see an error:

.. http:example:: ../belowthreshold/http/tutorial/delete-tender-doc-invalid.http
    :code:

