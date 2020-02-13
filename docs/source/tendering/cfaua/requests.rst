.. _cfaua_requests:

REST API specification
======================

Tender:
-------

* GET:
    `/tenders`

    Get tenders collection

    `/tenders/:tender_id`

    Get tender by id

* POST
    `/tenders:tender_id`

    Tender edit


Tender documents:
-----------------

* GET
    `/tenders/:tender_id/documents/:document_id`

    Tender Document Read

    `/tenders/:tender_id/documents`

    Tender Documents List

* PUT
    `/tenders/:tender_id/documents/:document_id`

    Tender Document Update

* POST
    `/tenders/:tender_id/documents`

    Tender Documents Upload

* PATCH
    `/tenders/:tender_id/documents/:document_id`

    Tender Document Update

Tender questions
----------------

* GET
    `/tenders/:tender_id/questions/:question_id`

    Retrieving the question

    `/tenders/:tender_id/questions`

    List of questions

* POST
    `/tenders/:tender_id/questions`

    Post a question

* PATCH
    `/tenders/:tender_id/questions/:question_id`

    Post an Answer

Tender qualifications
---------------------

* GET
    `/tenders/:tender_id/qualifications`

    List of qualifications

    `/tenders/:tender_id/qual…tions/:qualification_id`

    Retrieving the qualification

* PATCH
    `/tenders/:tender_id/qual…tions/:qualification_id`

    Post a qualification resolution

Tender qualifications complaints
--------------------------------

* GET
    `/tenders/:tender_id/qualifications/:qualification_id/complaints`

    List of complaint for award

    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id`

    Retrieving the complaint for award

* PATCH
    `/tenders/:tender_id/qualifications/:qualification_id/complaints`

    Post a complaint

Tender qualifications documents
-------------------------------

* PATCH
    `/tenders/:tender_id/qualifications/:qualification_id/documents/:document_id`

    Tender qualification document update

* POST

    `/tenders/:tender_id/qualifications/:qualification_id/documents`

    Tender qualification document upload

* PUT

    `/tenders/:tender_id/qualifications/:qualification_id/documents/:document_id`

    Tender qualification document update

* GET
    `/tenders/:tender_id/qualifications/:qualification_id/documents/:document_id`

    Tender qualification document read

    `/tenders/:tender_id/qualifications/:qualification_id/documents`

    Tender qualification documents list

Tender qualification complaint documents
----------------------------------------

* GET
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents/document_id`

    Tender award complaint document read

    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents`

    Tender award complaint documents list

* PUT
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents/:document_id`

    Tender award complaint document update

* POST
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents`

    Tender award complaint document upload

* PATCH
    `/tenders/:tender_id/qualifications/:qualification_id/complaints/:complaint_id/documents/:document_id`

    Tender award complaint document update

Tender lots
-----------

* GET
    `/tenders/:tender_id/lots`

    Lots listing

    `/tenders/:tender_id/lots/:lot_id`

    Retrieving the lot

* PATCH
    `/tenders/:tender_id/lots/:lot_id`

    Update of lot

* POST
    `/tenders/:tender_id/lots`

    Add a lot

* DELETE
    `/tenders/:tender_id/lots/:lot_id`

    Lot deleting

Tender cancellations
--------------------

* GET
    `/tenders/:tender_id/cancellations`

    List of cancellations

    `/tenders/:tender_id/cancellations/:cancellation_id`

    Retrieving cancellation

* PATCH
    `/tenders/:tender_id/cancellations/:cancellation_id`

    Post a cancellation resolution

* POST
    `/tenders/:tender_id/cancellations`

    Post a cancellation

Tender cancellation documents
-----------------------------

* GET
    `/tenders/:tender_id/cancellations/:cancellation_id/documents/:document_id`

    Tender cancellation document read

    `/tenders/:tender_id/cancellations/:cancellation_id/documents`

    Tender cancellation documents list

* POST
    `/tenders/:tender_id/cancellations/:cancellation_id/documents`

    Tender cancellation document upload

* PATCH
    `/tenders/:tender_id/cancellations/:cancellation_id/documents/:document_id`

    Tender cancellation document update

* PUT
    `/tenders/:tender_id/cancellations/:cancellation_id/documents/:document_id`

    Tender cancellation document update

Tender complaints
-----------------

* GET
    `/tenders/:tender_id/complaints`

    List of complaints

    `/tenders/:tender_id/complaints/:complaint_id`

    Retrieving the complaint

* POST
    `/tenders/:tender_id/complaints`

    Post a complaint

    `/tenders/:tender_id/complaints/:complaint_id`

    Retrieving the complaint

* PATCH
    `/tenders/:tender_id/complaints/:complaint_id`

    Post a complaint resolution

Tender bids
-----------

* GET
    `/tenders/:tender_id/bids/:bid_id`

    Retrieving the proposal

    `/tenders/:tender_id/bids`

    Bids Listing

* POST
    `/tenders/:tender_id/bids`

    Registration of new bid proposal

* PATCH
    `/tenders/:tender_id/bids/:bid_id`

    Update of proposal

* DELETE
    `/tenders/:tender_id/bids/:bid_id`

    Cancelling the proposal

Tender bid documents
--------------------

* GET
    `/tenders/:tender_id/bids/:bid_id/documents/:document_id`

    Tender bid document read

    `/tenders/:tender_id/bids/:bid_id/documents`

    Tender bid documents list

* POST
    `/tenders/:tender_id/bids/:bid_id/documents`

    Tender bid document upload

* PUT
    `/tenders/:tender_id/bids…/documents/:document_id`

    Tender bid document update

* PATCH
    /tenders/:tender_id/bids/:bid_id/documents/:document_id

    Tender bid document update

Tender bid eligibility documents
--------------------------------

* GET
    `/tenders/:tender_id/bids…_documents/:document_id`

    Tender bid document read

    `/tenders/:tender_id/bids/:bid_id/eligibility_documents`

    Tender bid documents list

* PATCH
    `/tenders/:tender_id/bids/:bid_id/eligibility_documents/:document_id`

    Tender bid document update

* PUT
    `/tenders/:tender_id/bids/:bid_id/eligibility_documents/:document_id`
    
    Tender bid document update

* POST
    `/tenders/:tender_id/bids/:bid_id/eligibility_documents`

    Tender bid document upload

Tender bid financial documents
------------------------------

* GET
    `/tenders/:tender_id/bids…_documents/:document_id`

    Tender bid document read

    `/tenders/:tender_id/bids…_id/financial_documents`

    Tender bid documents list

* POST
    `/tenders/:tender_id/bids/:bid_id/financial_documents`

    Tender bid document upload

* PATCH
    `/tenders/:tender_id/bids/:bid_id/financial_documents/:document_id`

    Tender bid document update

* PUT
    `/tenders/:tender_id/bids/:bid_id/financial_documents/:document_id`

    Tender bid document update

Tender bid qualification documents
----------------------------------

* GET
    `/tenders/:tender_id/bids/:bid_id/qualification_documents/:document_id`

    Tender bid document read

    `/tenders/:tender_id/bids/:bid_id/qualification_documents`

    Tender bid documents list

* POST
    `/tenders/:tender_id/bids/:bid_id/qualification_documents`

    Tender bid document upload

* PATCH
    `/tenders/:tender_id/bids/:bid_id/qualification_documents/:document_id`
    
    Tender bid document update

* PUT
    `/tenders/:tender_id/bids/:bid_id/qualification_documents/:document_id`
    
    Tender bid document update

Tender awards
-------------

* GET
    `/tenders/:tender_id/awards/:award_id`

    Retrieving the award

    `/tenders/:tender_id/awards`

    Tender Awards List

* PATCH
    `/tenders/:tender_id/awards/:award_id`

    Update of award

* POST
    `/tenders/:tender_id/awards`

    Accept or reject bidder application

Tender award documents
----------------------

* GET
    `/tenders/:tender_id/awar…/documents/:document_id`

    Tender award document read

    `/tenders/:tender_id/awards/:award_id/documents`

    Tender award documents list

* POST
    `/tenders/:tender_id/awards/:award_id/documents`

    Tender award document upload

* PUT
    `/tenders/:tender_id/awards/:award_id/documents/:document_id`

    Tender award document update

* PATCH
    `/tenders/:tender_id/awards/:award_id/documents/:document_id`

    Tender award document update

Tender award complaints
-----------------------

* GET
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id`

    Retrieving the complaint for award

    `/tenders/:tender_id/awards/:award_id/complaints`

    List complaints for award

* POST
    `/tenders/:tender_id/awards/:award_id/complaints`

    Post a complaint for award

* PATCH
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id`

    Patch a complaint for award

Tender award complaint documents
--------------------------------

* GET
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents/:document_id`

    Tender award complaint document read

    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents`

    Tender award complaint documents list

* POST
    `/tenders/:tender_id/awar…:complaint_id/documents`

    Tender award complaint document upload

* PATCH
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents/:document_id`

    Tender award complaint document update

* PUT
    `/tenders/:tender_id/awards/:award_id/complaints/:complaint_id/documents/:document_id`

    Tender award complaint document update

Tender auction
--------------

* GET
    `/tenders/:tender_id/auction`

    Get auction info

* POST
    `/tenders/:tender_id/auction`

    Report auction results

    `/tenders/:tender_id/auction/:auction_lot_id`

    Report auction results for lot

* PATCH
    `/tenders/:tender_id/auction`

    Set urls for access to auction

    `/tenders/:tender_id/auction/:auction_lot_id`

    Set url for access to auction for lot

Tender agreement
----------------

* GET
    `/tenders/:tender_id/agreements`

    List of agreements for award

* POST
    `/tenders/:tender_id/agreements`

    Post an agreement for award

* PATCH
    `/tenders/:tender_id/agreements/:agreement_id`

    Update of agreement

Tender agreement contract
-------------------------

* GET
    `/tenders/:tender_id/agreements/:agreement_id/contracts/:contract_id`
    
    Retrieving the contract for agreement

    `/tenders/:tender_id/agreements/:agreement_id/contracts`

    List of contracts for agreement

* PATCH
    `/tenders/:tender_id/agreements/:agreement_id/contracts/:contract_id`

    Update agreement contract

Tender agreement documents
--------------------------

* GET
    `/tenders/:tender_id/agreements/:agreement_id/documents/:document_id`

    Tender agreement document read

    `/tenders/:tender_id/agreements/:agreement_id/documents`

    Tender agreement documents list

* POST
    `/tenders/:tender_id/agreements/:agreement_id/documents`

    Tender agreement document upload

* PUT
    `/tenders/:tender_id/agreements/:agreement_id/documents/:document_id`

    Tender agreement document update

* PATCH
    `/tenders/:tender_id/agreements/:agreement_id/documents/:document_id`

    Tender agreement document update
