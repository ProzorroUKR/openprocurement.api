.. _tenders:

Retrieving Tender Information
=============================

Getting list of all tenders
---------------------------
.. sourcecode:: http

  GET /tenders HTTP/1.1

.. sourcecode:: http

  HTTP/1.1 200 OK

Sorting
~~~~~~~
Tenders retuned are sorted by modification time.

Limiting number of Tenders returned
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can control the number of `data` entries in the tenders feed (batch
size) with `limit` parameter. If not specified, data is being returned in
batches of 100 elements.

Batching
~~~~~~~~

The response contains `next_page` element with the following properties:

:offset:
    This is the parameter you have to add to the original request you made
    to get next page.

:path:
    This is path section of URL with original parameters and `offset`
    parameter added/replaced above.

:uri:
    The full version of URL for next page.

If next page request returns no data (i.e. empty array) then there is little
sense in fetching further pages.

Synchronizing
~~~~~~~~~~~~~

It is often necessary to be able to syncronize central database changes with
other database (we'll call it "local").  The default sorting "by
modification date" together with Batching mechanism allows one to implement
synchronization effectively.  The synchronization process can go page by
page until there is no new data returned.  Then the synchronizer has to
pause for a while to let central database register some changes and attempt
fetching subsequent page.  The `next_page` guarantees that all changes
from the last request are included in the new batch.

The safe frequency of synchronization requests is once per 5 minutes.
 
Reading the individual tender information
-----------------------------------------
.. sourcecode:: http

  GET /tenders/64e93250be76435397e8c992ed4214d1 HTTP/1.1

.. sourcecode:: http

  HTTP/1.1 200 OK

Reading the tender documents list
---------------------------------

.. sourcecode:: http

  GET /tenders/64e93250be76435397e8c992ed4214d1/documents HTTP/1.1

.. sourcecode:: http

  HTTP/1.1 200 OK

Example request:

.. http:example:: ../belowthreshold/http/tutorial/tender-documents-2.http
   :code:

Reading the tender document
---------------------------

The document can be retrieved by requesting the url returned in structures
from document list request in `data[*].url`.  It is safe to provide the
download URL to end user for download.
