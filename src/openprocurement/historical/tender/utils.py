from cornice.resource import resource
from functools import partial

from openprocurement.api.utils import error_handler
from openprocurement.historical.tender.traversal import historical_tender_factory
from openprocurement.historical.core.constants import PREDICATE_NAME

description = "Open Contracting compatible data exchange format. '\
                'See http://ocds.open-contracting.org/standard/r/master/#tender for more info"


tenders_history_resource = partial(
    resource,
    **{
        "error_handler": error_handler,
        "factory": historical_tender_factory,
        PREDICATE_NAME: "extract_doc_versioned",
        "description": description,
    }
)
