from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.procedure.utils import (
    save_tender,
    set_item,
)
from openprocurement.tender.core.procedure.serializers.agreement import AgreementSerializer
from logging import getLogger

LOGGER = getLogger(__name__)


def resolve_agreement(request):
    match_dict = request.matchdict
    if match_dict.get("agreement_id"):
        agreements = get_items(request, request.validated["tender"], "agreements", match_dict["agreement_id"])
        request.validated["agreement"] = agreements[0]


class TenderAgreementResource(TenderBaseResource):
    serializer_class = AgreementSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_agreement(request)

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        tender = self.request.validated["tender"]
        data = [self.serializer_class(b).data for b in tender.get("agreements", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated["agreement"]).data
        return {"data": data}

    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            agreement = self.request.validated["agreement"]
            self.state.validate_agreement_on_patch(agreement, updated)

            set_item(self.request.validated["tender"], "agreements", agreement["id"], updated)
            self.state.agreement_on_patch(agreement, updated)
            self.state.always(self.request.validated["tender"])

            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated tender agreement {}".format(agreement["id"]),
                    extra=context_unpack(self.request,
                                         {"MESSAGE_ID": "tender_agreement_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
