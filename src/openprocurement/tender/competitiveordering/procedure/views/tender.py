from cornice.resource import resource

from openprocurement.api.procedure.context import get_object
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.tender_details import (
    COLongTenderDetailsState,
    COShortTenderDetailsState,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tenders",
    accept="application/json",
)
class COTenderResource(TendersResource):
    state_class = None
    state_short_class = COShortTenderDetailsState
    state_long_class = COLongTenderDetailsState

    def __init__(self, request, context=None):
        self.state_short = self.state_short_class(request)
        self.state_long = self.state_long_class(request)
        super().__init__(request, context)

    @property
    def state(self):
        agreement = get_object("agreement")
        if not agreement:
            if "tender" not in self.request.validated:
                # POST: the agreement is fetched in collection_post, the request validation doesn't depend on it
                return self.state_long
            raise_operation_error(self.request, "Agreement not provided or not exist", status=422, name="agreements")
        agreement_has_items = bool(agreement.get("items"))
        if agreement_has_items:
            return self.state_short
        else:
            return self.state_long
