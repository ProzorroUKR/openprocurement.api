from copy import deepcopy
from hashlib import sha512

from openprocurement.api.utils import APIResource, json_view, context_unpack, get_now, generate_id
from openprocurement.framework.core.utils import (
    qualificationsresource,
    apply_patch,
    get_submission_by_id,
    generate_agreementID,
    save_agreement,
    get_agreement_by_id,
)
from openprocurement.framework.core.validation import (
    validate_patch_qualification_data,
    validate_update_qualification_in_not_allowed_status,
)
from openprocurement.framework.electroniccatalogue.models import Submission, Agreement
from openprocurement.framework.electroniccatalogue.utils import create_milestone


@qualificationsresource(
    name="electronicCatalogue:Qualifications",
    path="/qualifications/{qualification_id}",
    qualificationType="electronicCatalogue",
    description="",  # TODO: add description
)
class QualificationResource(APIResource):
    @json_view(permission="view_qualification")
    def get(self):
        """
        Get info by qualification
        """
        qualification_data = self.context.serialize("view")
        return {"data": qualification_data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_update_qualification_in_not_allowed_status,
            validate_patch_qualification_data,
        ),
        permission="edit_qualification",
    )
    def patch(self):
        """
        Qualification edit(partial)
        """
        qualification = self.request.context
        old_status = qualification.status
        new_status = self.request.validated["data"].get("status", old_status)
        changed_status = old_status != new_status
        if changed_status:
            qualification.date = get_now()
        apply_patch(self.request, src=self.request.validated["qualification_src"], obj_name="qualification")

        self.LOGGER.info("Updated qualification {}".format(qualification.id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"}))

        if changed_status:
            self.complete_submission()
        if old_status == "pending" and new_status == "active":
            self.ensure_agreement()
            self.create_agreement_contract()

        return {"data": qualification.serialize("view")}

    def complete_submission(self):
        db = self.request.registry.db
        qualification = self.request.validated["qualification"]
        submission_data = get_submission_by_id(db, qualification.submissionID)
        submission = Submission(submission_data)
        self.request.validated["submission_src"] = submission.serialize("plain")
        submission.status = "complete"
        self.request.validated["submission"] = submission
        apply_patch(self.request, src=self.request.validated["submission_src"], data=submission, obj_name="submission")
        self.LOGGER.info("Updated submission {}".format(submission.id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"}))

    def ensure_agreement(self):
        db = self.request.registry.db
        framework_data = self.request.validated["framework_src"]
        agreementID = framework_data.get("agreementID")
        if agreementID:
            agreement = get_agreement_by_id(db, agreementID)
            self.request.validated["agreement_src"] = agreement
            self.request.validated["agreement"] = Agreement(agreement)
        else:
            agreement_id = generate_id()
            now = get_now()
            transfer = generate_id()
            transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
            agreement_data = {
                "id": agreement_id,
                "agreementID": generate_agreementID(get_now(), db, self.server_id),
                "frameworkID": framework_data["_id"],
                "agreementType": framework_data["frameworkType"],
                "status": "active",
                "period": {
                    "startDate": now,
                    "endDate": framework_data["qualificationPeriod"]["endDate"]
                },
                "procuringEntity": framework_data["procuringEntity"],
                "classification": framework_data["classification"],
                "additionalClassifications": framework_data["additionalClassifications"],
                "contracts": [],
                "owner": framework_data["owner"],
                "owner_token": framework_data["owner_token"],
                "mode": framework_data.get("type"),
                "dateModified": now,
                "date": now,
                "transfer_token": transfer_token,
            }
            agreement = Agreement(agreement_data)

            self.request.validated["agreement_src"] = {}
            self.request.validated["agreement"] = agreement
            if save_agreement(self.request):
                self.LOGGER.info(
                    "Created agreement {}".format(agreement_id),
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "agreement_create"},
                        {"agreement_id": agreement_id,
                         "agreement_mode": agreement.mode},
                    ),
                )

                framework_data_updated = dict(framework_data, agreementID=agreement_id)
                apply_patch(
                    self.request, data=framework_data_updated, src=self.request.validated["framework_src"],
                    obj_name="framework"
                )
                self.LOGGER.info("Updated framework {} with agreementID".format(framework_data["_id"]),
                                 extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"}))

    def create_agreement_contract(self):
        db = self.request.registry.db
        qualification = self.request.validated["qualification"]
        framework = self.request.validated["framework"]
        agreement_data = get_agreement_by_id(db, framework.agreementID)
        submission_data = get_submission_by_id(db, qualification.submissionID)

        contract_id = generate_id()
        first_milestone = create_milestone(
            documents=qualification.documents, framework=self.request.validated["framework_src"]
        )
        contract_data = {
            "id": contract_id,
            "qualificationID": qualification.id,
            "status": "active",
            "suppliers": submission_data["tenderers"],
            "milestones": [first_milestone],
        }
        new_contracts = deepcopy(agreement_data.get("contracts", []))
        new_contracts.append(contract_data)

        apply_patch(self.request, data={"contracts": new_contracts}, src=agreement_data, obj_name="agreement")
        self.LOGGER.info("Updated agreement {} with contract {}".format(agreement_data["_id"], contract_id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"}))
