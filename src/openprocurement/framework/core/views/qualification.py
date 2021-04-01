from openprocurement.api.utils import (
    APIResourceListing,
)
from openprocurement.framework.core.design import (
    QUALIFICATION_FIELDS,
    qualifications_by_dateModified_view,
    qualifications_test_by_dateModified_view,
    qualifications_by_local_seq_view,
    qualifications_test_by_local_seq_view,
)
from openprocurement.framework.core.utils import (
    qualificationsresource,
)

VIEW_MAP = {
    "": qualifications_by_dateModified_view,
    "test": qualifications_test_by_dateModified_view,
    "_all_": qualifications_by_dateModified_view,

}
CHANGES_VIEW_MAP = {
    "": qualifications_by_local_seq_view,
    "test": qualifications_test_by_local_seq_view,
    "_all_": qualifications_by_local_seq_view,
}
FEED = {"dateModified": VIEW_MAP, "changes": CHANGES_VIEW_MAP}


@qualificationsresource(
    name="Qualifications",
    path="/qualifications",
    description="",  # TODO: Add description
)
class QualificationResource(APIResourceListing):
    def __init__(self, request, context):
        super(QualificationResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = QUALIFICATION_FIELDS
        # self.serialize_func = tender_serialize
        self.object_name_for_listing = "Qualifications"
        self.log_message_id = "qualification_list_custom"
        self.db = request.registry.databases.qualifications
