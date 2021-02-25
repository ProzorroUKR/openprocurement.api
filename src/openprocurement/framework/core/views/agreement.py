# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    generate_id,
    json_view,
    set_ownership,
    get_now,
    upload_objects_documents,
    context_unpack,
    APIResourceListing,
)
from openprocurement.framework.core.design import (
    AGREEMENT_FIELDS,
    agreements_real_by_dateModified_view,
    agreements_test_by_dateModified_view,
    agreements_by_dateModified_view,
    agreements_real_by_local_seq_view,
    agreements_test_by_local_seq_view,
    agreements_by_local_seq_view,
)
from openprocurement.framework.core.utils import (
    generate_agreementID,
    save_agreement,
    agreement_serialize,
    agreementsresource,
)
from openprocurement.framework.core.validation import validate_agreement_data

VIEW_MAP = {
    u"": agreements_real_by_dateModified_view,
    u"test": agreements_test_by_dateModified_view,
    u"_all_": agreements_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u"": agreements_real_by_local_seq_view,
    u"test": agreements_test_by_local_seq_view,
    u"_all_": agreements_by_local_seq_view,
}
FEED = {u"dateModified": VIEW_MAP, u"changes": CHANGES_VIEW_MAP}


@agreementsresource(name="Agreements", path="/agreements")
class AgreementResource(APIResourceListing):
    def __init__(self, request, context):
        super(AgreementResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = AGREEMENT_FIELDS
        self.serialize_func = agreement_serialize
        self.object_name_for_listing = "Agreements"
        self.log_message_id = "agreement_list_custom"

    @json_view(content_type="application/json", permission="create_agreement", validators=(validate_agreement_data,))
    def post(self):
        agreement = self.request.validated["agreement"]
        if not agreement.id:
            agreement_id = generate_id()
            agreement.id = agreement_id
        if not agreement.get("agreementID"):
            agreement.prettyID = generate_agreementID(get_now(), self.db, self.server_id)

        # Unify when cfa moved from tenders to frameworks
        framework = self.request.validated.get("framework")
        if framework:
            agreement.submissionType = framework["frameworkType"]
            agreement.mode = framework.get("mode")
            upload_objects_documents(
                self.request, agreement,
                route_kwargs={"agreement_id": agreement.id},
                route_prefix=framework["frameworkType"]
            )

        access = set_ownership(agreement, self.request)
        self.request.validated["agreement"] = agreement
        self.request.validated["agreement_src"] = {}
        if save_agreement(self.request):
            self.LOGGER.info(
                "Created agreement {} ({})".format(agreement.id, agreement.agreementID),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "agreement_create"},
                    {"agreement_id": agreement.id, "agreementID": agreement.agreementID},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}.Agreement".format(agreement.agreementType), agreement_id=agreement.id
            )
            return {"data": agreement.serialize("view"), "access": access}
