.. _pricequotation_overview:

Overview
========

The Open Procurement `Price Quotation` procedure is plugin to `Open Procurement API` software.

REST-ful interface to plugin is in line with core software design principles. 

Main responsibilities
---------------------

Price Quotation procedure is dedicated to Open Tender procedure for Ukrainian below threshold procurements.  The code for that type of procedure is `priceQuotation`.

Business logic
--------------

1) Publication of the Price Quotation

Business process begins when the Procuring Entity creates a Price Quotation procedure using parameters from the e-Catalogues Profile database. 

After Procuring Entity supplements the procedure with quantity of items and delivery details and publishes the tender by sending a request for Price Quotation to ProZorro Business Process Engine the process starts.

At this moment Business Process Engine receives and validates the Price Quotation request. Given the validation is passed the system automatically informs shortlisted (qualified to specific eCatalogue Profile) suppliers about the request.

2) Tendering

Receiving a Price Quotation request, supplier decides if they are able to offer the requested product. In case of rejection supplier declines participation in procedure.
Until the end of tender period (minimal two working days) suppliers would be able to submit a bid, while BPE will collect and register quotations. 

3) Awarding, Qualification

After the deadline system will publish received bids, awarding suppleir with most economically advantageous bid allowing to confirm award within two business days. In case if award was not confirmed system will automatically award next supplier providing same confirmation period. In case of no suppliers left system will transfer procedure to status `unsuccessful`.

4) Contracting

Selecting a winner will lead both Procuring Entity and supplier to the contracting process, where the contract is signed, published and taken to execution.
