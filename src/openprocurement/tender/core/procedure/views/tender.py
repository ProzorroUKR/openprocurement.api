from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context,
)
from openprocurement.api.views.base import MongodbResourceListing, RestrictedResourceListingMixin
from openprocurement.api.mask_deprecated import mask_object_data_deprecated
from openprocurement.api.mask import mask_object_data
from openprocurement.framework.core.utils import request_fetch_agreement
from openprocurement.tender.core.procedure.context import (
    get_tender_config,
    get_tender,
)
from openprocurement.tender.core.procedure.utils import (
    set_ownership,
    save_tender,
)
from openprocurement.tender.core.procedure.schema.ocds import ocds_format_tender
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.serializers.tender import TenderBaseSerializer
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from pyramid.security import (
    Allow,
    Everyone,
)
from cornice.resource import resource
import logging

from openprocurement.tender.core.utils import ProcurementMethodTypePredicate

LOGGER = logging.getLogger(__name__)


@resource(
    name="Tenders",
    path="/tenders",
    description="Tender listing",
    request_method=("GET",),  # all "GET /tenders" requests go here
)
class TendersListResource(RestrictedResourceListingMixin, MongodbResourceListing):
    listing_name = "Tenders"
    listing_default_fields = {"dateModified"}
    listing_allowed_fields = {
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
    mask_deprecated_required_fields = {"is_masked", "procuringEntity"}
    mask_mapping = TENDER_MASK_MAPPING

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.db_listing_method = request.registry.mongodb.tenders.list

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl

    def db_fields(self, fields):
        fields = super().db_fields(fields)
        return fields | self.mask_deprecated_required_fields

    def filter_results_fields(self, results, fields):
        for r in results:
            mask_object_data_deprecated(self.request, r)
        return super().filter_results_fields(results, fields)


class TendersResource(TenderBaseResource):
    serializer_class = TenderBaseSerializer

    def collection_post(self):
        update_logging_context(self.request, {"tender_id": "__new__"})
        tender = self.request.validated["data"]
        agreements = tender.get("agreements")
        if agreements and "agreement" not in self.request.validated:
            request_fetch_agreement(self.request, agreements[0]["id"], raise_error=False)
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
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tenders".format(route_prefix),
                tender_id=tender["_id"],
            )
            return {
                "data": self.serializer_class(get_tender()).data,
                "config": get_tender_config(),
                "access": access,
            }

    @json_view(permission="view_tender")
    def get(self):
        data = self.serializer_class(get_tender()).data
        # convert to different schemas, for ex. OCDS-1.1
        # https://standard.open-contracting.org/latest/en/schema/release_package/
        schema = self.request.params.get("opt_schema", "")
        if "ocds" in schema.lower():
            if "plans" in data:
                plan_id = data['plans'][0]['id']
                plan = self.request.registry.mongodb.plans.get(plan_id)
            else:
                plan = None
            data = ocds_format_tender(
                tender=data,
                tender_url=self.request.url,
                plan=plan
            )
            return data
        return {
            "data": data,
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
