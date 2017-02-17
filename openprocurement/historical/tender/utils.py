from cornice.resource import resource
from functools import partial

from openprocurement.api.utils import error_handler
from openprocurement.historical.tender.traversal import (
    historical_tender_factory
)


tenders_history_resource = partial(resource,
                                   error_handler=error_handler,
                                   factory=historical_tender_factory)
