from logging import getLogger

from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.procedure.context import get_qualification
from openprocurement.api.utils import (
    json_view,
    request_fetch_agreement,
    request_fetch_submission,
)
from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.framework.core.procedure.mask import QUALIFICATION_MASK_MAPPING
from openprocurement.framework.core.procedure.serializers.qualification import (
    QualificationSerializer,
)
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource

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
        "public_modified",
        "public_ts",
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
        qualification = get_qualification()
        return {
            "data": self.serializer_class(qualification).data,
            "config": qualification["config"],
        }

    def patch(self):
        updated = self.request.validated["data"]
        qualification = self.request.validated["qualification"]
        qualification_src = self.request.validated["qualification_src"]
        if updated:
            qualification = self.request.validated["qualification"] = updated

            # fetch related data
            request_fetch_submission(self.request, updated["submissionID"])
            framework = self.request.validated["framework"]
            if agreement_id := framework.get("agreementID"):
                request_fetch_agreement(self.request, agreement_id)

            self.state.qualification.on_patch(qualification_src, qualification)

            # save all
            self.save_all_objects()
        return {
            "data": self.serializer_class(qualification).data,
            "config": qualification["config"],
        }
