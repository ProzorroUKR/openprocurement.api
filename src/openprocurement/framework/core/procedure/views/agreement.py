from logging import getLogger
from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context,
)
from openprocurement.api.views.base import MongodbResourceListing, RestrictedResourceListingMixin
from openprocurement.framework.core.procedure.mask import AGREEMENT_MASK_MAPPING
from openprocurement.framework.core.procedure.serializers.agreement import AgreementSerializer
from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.core.procedure.context import get_object_config, get_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.tender.core.procedure.utils import set_ownership

LOGGER = getLogger(__name__)


@resource(
    name="Agreements",
    path="/agreements",
    description="Agreement listing",
    request_method=("GET",),
)
class AgreementsListResource(RestrictedResourceListingMixin, MongodbResourceListing):
    listing_name = "Agreements"
    listing_default_fields = {
        "dateModified",
    }
    listing_allowed_fields = {
        "dateCreated",
        "dateModified",
        "id",
        "agreementID",
        "agreementType",
        "status",
        "tender_id",
        "next_check",
        "procuringEntity",
    }
    mask_mapping = AGREEMENT_MASK_MAPPING

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.db_listing_method = request.registry.mongodb.agreements.list

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


class AgreementsResource(FrameworkBaseResource):
    serializer_class = AgreementSerializer
    state_class = AgreementState

    def collection_post(self):
        update_logging_context(self.request, {"agreement_id": "__new__"})
        agreement = self.request.validated["data"]
        self.state.on_post(agreement)
        access = set_ownership(agreement, self.request)
        self.state.on_post(agreement)
        self.request.validated["agreement"] = agreement
        self.request.validated["agreement_src"] = {}
        if save_object(self.request, "agreement", insert=True):
            LOGGER.info(
                f"Created agreement {agreement['_id']} ({agreement['agreementID']})",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "submission_create"},
                    {
                        "agreement_id": agreement["_id"],
                        "agreementID": agreement["agreementID"],
                    },
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                f"{agreement['agreementType']}:Agreements", agreement_id=agreement["_id"]
            )
            return {
                "data": self.serializer_class(agreement).data,
                "access": access,
            }

    @json_view(
        permission="view_framework",
    )
    def get(self):
        return {
            "data": self.serializer_class(get_object("agreement")).data,
            "config": get_object_config("agreement"),
        }

    def patch(self):
        updated = self.request.validated["data"]
        if self.request.authenticated_role == "chronograph":
            agreement = self.request.validated["agreement"]
            self.state.patch_statuses_by_chronograph(agreement)
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    "Updated agreement by chronograph",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_chronograph_patch"})
                )
        elif updated:
            self.request.validated["agreement"] = updated
            self.state.on_patch(self.request.validated["agreement_src"], updated)
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    f"Updated agreement {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"})
                )
        return {
            "data": self.serializer_class(get_object("agreement")).data,
            "config": get_object_config("agreement"),
        }


@resource(
    name="Agreements by classificationID",
    path="/agreements_by_classification/{classification_id}",
    description="Agreements filter classification"
)
class AgreementFilterByClassificationResource(FrameworkBaseResource):

    @json_view(permission="view_framework")
    def get(self):
        classification_id = self.request.matchdict.get("classification_id")
        if "-" in classification_id:
            classification_id = classification_id[:classification_id.find("-")]
        additional_classifications = self.request.params.get("additional_classifications", "")

        if additional_classifications.lower() == "none":
            additional_classifications = set()
        elif additional_classifications:
            additional_classifications = set(additional_classifications.split(","))

        results = self.request.registry.mongodb.agreements.list_by_classification_id(classification_id)
        if isinstance(additional_classifications, set):
            results = [
                x for x in results
                if {i['id'] for i in x.get("additionalClassifications", "")} == additional_classifications
            ]

        return {"data": results}
