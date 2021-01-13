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
    u"": qualifications_by_dateModified_view,
    u"test": qualifications_test_by_dateModified_view,
    u"_all_": qualifications_by_dateModified_view,

}
CHANGES_VIEW_MAP = {
    u"": qualifications_by_local_seq_view,
    u"test": qualifications_test_by_local_seq_view,
    u"_all_": qualifications_by_local_seq_view,
}
FEED = {u"dateModified": VIEW_MAP, u"changes": CHANGES_VIEW_MAP}


@qualificationsresource(
    name="Qualification",
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
        self.object_name_for_listing = "Qualification"
        self.log_message_id = "qualification_list_custom"
