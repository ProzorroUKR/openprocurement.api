from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context,
)
from openprocurement.api.views.base import MongodbResourceListing
from openprocurement.tender.core.procedure.context import (
    get_tender_config,
    get_tender,
)
from openprocurement.tender.core.procedure.utils import (
    set_ownership,
    save_tender,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.serializers.tender import TenderBaseSerializer
from pyramid.security import (
    Allow,
    Everyone,
)
from cornice.resource import resource
import logging

LOGGER = logging.getLogger(__name__)


@resource(
    name="Tenders",
    path="/tenders",
    description="Tender listing",
    request_method=("GET",),  # all "GET /tenders" requests go here
)
class TendersListResource(MongodbResourceListing):

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.listing_name = "Tenders"
        self.listing_default_fields = {"dateModified"}
        self.listing_allowed_fields = {
            "dateCreated",
            "dateModified",
            "qualificationPeriod",
            "auctionPeriod",
            "awardPeriod",
            "status",
            "tenderID",
            "lots",
            "contracts",
            "agreements",
            "procuringEntity",
            "procurementMethodType",
            "procurementMethod",
            "next_check",
            "mode",
            "stage2TenderID",
        }
        self.db_listing_method = request.registry.mongodb.tenders.list

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
        self._serialize_config(self.request, get_tender_config())
        access = set_ownership(tender, self.request)
        self.state.on_post(tender)
        self.request.validated["tender"] = tender
        self.request.validated["tender_src"] = {}
        if save_tender(self.request, insert=True):
            LOGGER.info(
                "Created tender {} ({})".format(tender["_id"], tender["tenderID"]),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_create"},
                    {
                        "tender_id": tender["_id"],
                        "tenderID": tender["tenderID"],
                        "tender_mode": tender.get("mode"),
                    },
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tenders".format(tender["procurementMethodType"]), tender_id=tender["_id"]
            )
            return {
                "data": self.serializer_class(get_tender()).data,
                "config": get_tender_config(),
                "access": access,
            }

    @json_view(permission="view_tender")
    def get(self):
        return {
            "data": self.serializer_class(get_tender()).data,
            "config": get_tender_config(),
        }

    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            before = self.request.validated["tender_src"]
            self.state.validate_tender_patch(before, updated)
            self.request.validated["tender"] = updated
            self.state.on_patch(self.request.validated["tender_src"], updated)
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
                )
        return {
            "data": self.serializer_class(get_tender()).data,
            "config": get_tender_config(),
        }
