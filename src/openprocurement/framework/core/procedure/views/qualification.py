from logging import getLogger
from cornice.resource import resource
from pyramid.security import Allow, Everyone
from openprocurement.api.utils import json_view
from openprocurement.api.views.base import MongodbResourceListing, RestrictedResourceListingMixin
from openprocurement.framework.core.procedure.mask import QUALIFICATION_MASK_MAPPING
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.context import get_object_config, get_object
from openprocurement.framework.core.procedure.serializers.qualification import QualificationSerializer
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.utils import request_fetch_submission, request_fetch_agreement

LOGGER = getLogger(__name__)


@resource(
    name="Qualifications",
    path="/qualifications",
    description="Qualification listing",
    request_method=("GET",),
)
class QualificationsListResource(RestrictedResourceListingMixin, MongodbResourceListing):
    listing_name = "Qualifications"
    listing_default_fields = {
        "dateModified",
    }
    listing_allowed_fields = {
        "dateModified",
        "dateCreated",
        "id",
        "frameworkID",
        "submissionID",
        "qualificationType",
        "status",
        "documents",
        "date",
    }
    mask_mapping = QUALIFICATION_MASK_MAPPING

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.db_listing_method = request.registry.mongodb.qualifications.list

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


class QualificationsResource(FrameworkBaseResource):
    LOGGER = LOGGER
    serializer_class = QualificationSerializer
    state_class = FrameworkState

    @json_view(
        permission="view_framework",
    )
    def get(self):
        return {
            "data": self.serializer_class(get_object("qualification")).data,
            "config": get_object_config("qualification"),
        }

    def patch(self):
        request = self.request
        updated = request.validated["data"]
        if updated:
            request.validated["qualification"] = updated
            before = request.validated["qualification_src"]

            # fetch related data
            request_fetch_submission(request, updated["submissionID"])
            framework_data = request.validated["framework"]
            if agreement_id := framework_data.get("agreementID"):
                request_fetch_agreement(request, agreement_id)

            self.state.qualification.on_patch(before, updated)

            # save all
            self.save_all_objects()
        return {
            "data": self.serializer_class(get_object("qualification")).data,
            "config": get_object_config("qualification"),
        }
