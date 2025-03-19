from logging import getLogger

from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.procedure.context import get_agreement
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    raise_operation_error,
    request_init_agreement,
    update_logging_context,
)
from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.framework.core.procedure.mask import AGREEMENT_MASK_MAPPING
from openprocurement.framework.core.procedure.serializers.agreement import (
    AgreementSerializer,
)
from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
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
        request_init_agreement(self.request, agreement, agreement_src={})
        self.state.on_post(agreement)
        access = set_ownership(agreement, self.request)
        self.state.on_post(agreement)
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
                f"{agreement['agreementType']}:Agreements",
                agreement_id=agreement["_id"],
            )
            return {
                "data": self.serializer_class(agreement).data,
                "config": agreement["config"],
                "access": access,
            }

    @json_view(
        permission="view_framework",
    )
    def get(self):
        agreement = get_agreement()
        return {
            "data": self.serializer_class(agreement).data,
            "config": agreement["config"],
        }

    def patch(self):
        updated = self.request.validated["data"]
        agreement = self.request.validated["agreement"]
        agreement_src = self.request.validated["agreement_src"]
        if self.request.authenticated_role == "chronograph":
            self.state.on_chronograph_patch(agreement)
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    "Updated agreement by chronograph",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_chronograph_patch"}),
                )
        elif updated:
            agreement = self.request.validated["agreement"] = updated
            self.state.on_patch(agreement_src, agreement)
            if save_object(self.request, "agreement"):
                self.LOGGER.info(
                    f"Updated agreement {agreement['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}),
                )
        return {
            "data": self.serializer_class(agreement).data,
            "config": agreement["config"],
        }


@resource(
    name="Agreements by classificationID",
    path="/agreements_by_classification/{classification_id}",
    description="Agreements filter classification",
)
class AgreementFilterByClassificationResource(FrameworkBaseResource):
    MIN_CLASSIFICATION_ID_LENGTH = 3

    @json_view(permission="view_framework")
    def get(self):
        classification_id = self._prepare_classification_id()
        results = self.request.registry.mongodb.agreements.list_by_classification_id(classification_id)
        results = self._filter_by_additional_classifications(results)
        return {"data": results}

    def _prepare_classification_id(self):
        classification_id = self.request.matchdict.get("classification_id")
        classification_id = classification_id.split("-")[0]
        classification_id = classification_id.strip()

        if len(classification_id) < self.MIN_CLASSIFICATION_ID_LENGTH:
            raise_operation_error(
                self.request,
                f"classification id must be at least {self.MIN_CLASSIFICATION_ID_LENGTH} characters long",
                status=422,
            )
        return classification_id

    def _filter_by_additional_classifications(self, results):
        additional_classifications = self.request.params.get("additional_classifications", "")
        if not additional_classifications:
            return results

        if additional_classifications.lower() == "none":
            additional_classifications = set()
        else:
            additional_classifications = set(additional_classifications.split(","))

        return [
            result
            for result in results
            if {i["id"] for i in result.get("additionalClassifications", [])} == additional_classifications
        ]
