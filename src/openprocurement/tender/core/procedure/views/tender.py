from openprocurement.tender.core.design import (
    FIELDS,
    tenders_by_dateModified_view,
    tenders_real_by_dateModified_view,
    tenders_test_by_dateModified_view,
    tenders_by_local_seq_view,
    tenders_real_by_local_seq_view,
    tenders_test_by_local_seq_view,
)
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResourceListing,
    update_logging_context,
)
from openprocurement.tender.core.utils import tender_serialize
from openprocurement.tender.core.procedure.utils import (
    set_ownership,
    save_tender,
    set_mode_test_titles,
    apply_tender_patch,
    apply_data_patch,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.serializers.tender import TenderBaseSerializer
from pyramid.security import Allow, Everyone
from cornice.resource import resource
import logging


LOGGER = logging.getLogger(__name__)

VIEW_MAP = {
    "": tenders_real_by_dateModified_view,
    "test": tenders_test_by_dateModified_view,
    "_all_": tenders_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    "": tenders_real_by_local_seq_view,
    "test": tenders_test_by_local_seq_view,
    "_all_": tenders_by_local_seq_view,
}
FEED = {"dateModified": VIEW_MAP, "changes": CHANGES_VIEW_MAP}


@resource(
    name="Tenders",
    path="/tenders",
    description="Tender listing",
    request_method=("GET",),  # all "GET /tenders" requests go here
)
class TendersListResource(APIResourceListing):
    VIEW_MAP = VIEW_MAP
    CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
    FEED = FEED
    FIELDS = FIELDS
    serialize_func = tender_serialize
    object_name_for_listing = "Tenders"
    log_message_id = "tender_list_custom"

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


class TendersResource(TenderBaseResource):
    serializer_class = TenderBaseSerializer

    def collection_post(self):
        update_logging_context(self.request, {"tender_id": "__new__"})
        tender = self.request.validated["data"]
        access = set_ownership(tender, self.request)
        self.state.on_post(tender)

        if tender.get("mode") == "test":
            set_mode_test_titles(tender)

        self.request.validated["tender"] = tender
        self.request.validated["tender_src"] = {}
        if save_tender(self.request):
            LOGGER.info(
                "Created tender {} ({})".format(tender["_id"], tender["tenderID"]),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_create"},
                    {"tender_id": tender["_id"],
                     "tenderID": tender["tenderID"],
                     "tender_mode": tender.get("mode")},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tenders".format(tender["procurementMethodType"]), tender_id=tender["_id"]
            )
            return {"data": self.serializer_class(tender).data, "access": access}

    @json_view(permission="view_tender")
    def get(self):
        tender = self.request.validated["tender"]
        return {"data": self.serializer_class(tender).data}

    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            self.request.validated["tender"] = updated
            self.state.on_patch(self.request.validated["tender_src"], updated)
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
                )
        return {"data": self.serializer_class(self.request.validated["tender"]).data}
