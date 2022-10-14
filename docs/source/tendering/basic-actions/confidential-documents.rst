
.. _confidential-documents:


Confidential documents
======================

Confidential documents are supported for bids in the above threshold procedures.


Confidentiality
---------------

Documents can be either public or private:

  1. Privacy settings can be changed only for the latest version of the document.
  2. When you upload new version of the document, privacy settings are copied from the previous version.
  3. Privacy settings can be changed only during `tenderPeriod` (with `active.tendering` status).
  4. If tender has status `active.qualification` winner can upload only public documents.


Tutorial
--------


Let's upload a private document


.. http:example:: ./http/confidential-documents/create-document.http
   :code:


`confidentiality` can be changed during `active.tendering` tender status

.. http:example:: ./http/confidential-documents/patch-public-document.http
   :code:


The confidential documents shown without the `url` field

.. http:example:: ./http/confidential-documents/document-list-public.http
   :code:


Only tender and bid owner should see the `url` fields and be able to download confidential documents

.. http:example:: ./http/confidential-documents/document-list-private.http
   :code:
