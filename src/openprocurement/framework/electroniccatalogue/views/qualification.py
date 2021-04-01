from copy import deepcopy
from hashlib import sha512

from openprocurement.api.utils import (
    APIResource, json_view, context_unpack, get_now, generate_id, raise_operation_error,
)
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
        qualification = self.request.validated["qualification"]
        submission_data = get_submission_by_id(self.request, qualification.submissionID)
        submission = Submission(submission_data)
        self.request.validated["submission_src"] = submission.serialize("plain")
        submission.status = "complete"
        self.request.validated["submission"] = submission
        apply_patch(self.request, src=self.request.validated["submission_src"], data=submission, obj_name="submission")
        self.LOGGER.info("Updated submission {}".format(submission.id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"}))

    def ensure_agreement(self):
        framework_data = self.request.validated["framework_src"]
        agreementID = framework_data.get("agreementID")
        if agreementID:
            agreement = get_agreement_by_id(self.request, agreementID)
            if not agreement:
                raise_operation_error(
                    self.request,
                    "agreementID must be one of exists agreement",
                )
            self.request.validated["agreement"] = agreement = Agreement(agreement)
            agreement.__parent__ = self.request.validated["qualification"].__parent__
            self.request.validated["agreement_src"] = agreement.serialize("plain")
        else:
            agreement_id = generate_id()
            now = get_now()
            transfer = generate_id()
            transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
            agreement_data = {
                "id": agreement_id,
                "agreementID": generate_agreementID(get_now(), self.request.registry.databases.agreements,
                                                    self.server_id),
                "frameworkID": framework_data["id"],
                "agreementType": framework_data["frameworkType"],
                "status": "active",
                "period": {
                    "startDate": now,
                    "endDate": framework_data.get("qualificationPeriod").get("endDate")
                },
                "procuringEntity": framework_data.get("procuringEntity"),
                "classification": framework_data.get("classification"),
                "additionalClassifications": framework_data.get("additionalClassifications"),
                "contracts": [],
                "owner": framework_data["owner"],
                "owner_token": framework_data["owner_token"],
                "mode": framework_data.get("type"),
                "dateModified": now,
                "date": now,
                "transfer_token": transfer_token,
                "frameworkDetails": framework_data.get("frameworkDetails"),
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

                framework_data_updated = {"agreementID": agreement_id}
                apply_patch(
                    self.request, data=framework_data_updated, src=self.request.validated["framework_src"],
                    obj_name="framework"
                )
                self.LOGGER.info("Updated framework {} with agreementID".format(framework_data["id"]),
                                 extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"}))

    def create_agreement_contract(self):
        qualification = self.request.validated["qualification"]
        framework = self.request.validated["framework"]
        agreement_data = get_agreement_by_id(self.request, framework.agreementID)
        if not agreement_data:
            raise_operation_error(
                self.request,
                "agreementID must be one of exists agreement",
            )
        submission_data = get_submission_by_id(self.request, qualification.submissionID)
        if not agreement_data:
            raise_operation_error(
                self.request,
                "submissionID must be one of exists submission",
            )
        if agreement_data["status"] != "active":
            return

        contract_id = generate_id()
        first_milestone_data = {
            "type": "activation",
            "documents": qualification.documents
        }
        contract_data = {
            "id": contract_id,
            "qualificationID": qualification.id,
            "status": "active",
            "suppliers": submission_data["tenderers"],
            "milestones": [first_milestone_data],
        }
        new_contracts = deepcopy(agreement_data.get("contracts", []))
        new_contracts.append(contract_data)

        apply_patch(self.request, data={"contracts": new_contracts}, src=agreement_data, obj_name="agreement")
        self.LOGGER.info("Updated agreement {} with contract {}".format(agreement_data["_id"], contract_id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"}))
