from openprocurement.api.utils import (
    generate_id,
    json_view,
    set_ownership,
    get_now,
    upload_objects_documents,
    context_unpack,
)
from openprocurement.api.views.base import MongodbResourceListing
from openprocurement.framework.core.utils import (
    generate_agreementID,
    save_agreement,
    agreementsresource,
)
from openprocurement.framework.core.validation import validate_agreement_data


@agreementsresource(name="Agreements", path="/agreements")
class AgreementResource(MongodbResourceListing):
    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "Agreements"
        self.listing_default_fields = {"dateModified"}
        self.all_fields = {"dateCreated", "dateModified", "id", "agreementID",
                           "agreementType", "status", "tender_id", "next_check"}
        self.db_listing_method = request.registry.mongodb.agreements.list

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
        if save_agreement(self.request, insert=True):
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
