from openprocurement.api.utils import (
    APIResourceListing,
    json_view,
    generate_id,
    get_now,
    set_ownership,
    context_unpack,
)
from openprocurement.framework.core.design import (
    FIELDS,
    frameworks_by_dateModified_view,
    frameworks_test_by_dateModified_view,
    frameworks_by_local_seq_view,
    frameworks_test_by_local_seq_view,
    frameworks_real_by_local_seq_view,
    frameworks_real_by_dateModified_view,
)
from openprocurement.framework.core.utils import (
    frameworksresource,
    generate_framework_pretty_id,
    save_framework,
    framework_serialize,
)
from openprocurement.framework.core.validation import validate_framework_data

VIEW_MAP = {
    u"": frameworks_real_by_dateModified_view,
    u"test": frameworks_test_by_dateModified_view,
    u"_all_": frameworks_by_dateModified_view,

}
CHANGES_VIEW_MAP = {
    u"": frameworks_real_by_local_seq_view,
    u"test": frameworks_test_by_local_seq_view,
    u"_all_": frameworks_by_local_seq_view,
}
FEED = {u"dateModified": VIEW_MAP, u"changes": CHANGES_VIEW_MAP}


@frameworksresource(
    name="Frameworks",
    path="/frameworks",
    description="",  # TODO: Add description
)
class FrameworkResource(APIResourceListing):
    def __init__(self, request, context):
        super(FrameworkResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = framework_serialize
        self.object_name_for_listing = "Frameworks"
        self.log_message_id = "framework_list_custom"

    @json_view(
        content_type="application/json",
        permission="create_framework",
        validators=(
                validate_framework_data,
        )
    )
    def post(self):
        """"""  # TODO: Add description
        framework_id = generate_id()
        framework = self.request.validated["framework"]
        framework.id = framework_id
        if not framework.get("prettyID"):
            framework.prettyID = generate_framework_pretty_id(get_now(), self.db, self.server_id)
        access = set_ownership(framework, self.request)
        self.request.validated["framework"] = framework
        self.request.validated["framework_src"] = {}
        if save_framework(self.request):
            self.LOGGER.info(
                "Created tender {} ({})".format(framework_id, framework.prettyID),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "framework_create"},
                    {"framework_id": framework_id, "prettyID": framework.prettyID,
                     "framework_mode": framework.mode},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Framework".format(framework.frameworkType), framework_id=framework_id
            )
            return {"data": framework.serialize(framework.status), "access": access}
