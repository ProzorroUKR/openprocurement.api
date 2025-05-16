from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_complaint
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)


class ComplaintAppealValidationsMixin:
    def validate_tender_status(self):
        tender = get_tender()
        tender_statue = tender.get("status")
        if tender_statue in ("complete", "unsuccessful", "cancelled"):
            raise_operation_error(
                self.request,
                f"Can't submit or edit appeal in current ({tender_statue}) tender status",
            )

    def validate_complaint_type(self, complaint):
        if complaint.get("type") != "complaint":
            raise_operation_error(
                self.request,
                f"Can't submit or edit appeal in current ({complaint.get('type')}) complaint type",
            )

    def validate_complaint_status(self, complaint):
        complaint_status = complaint.get("status")
        if complaint_status not in ("invalid", "satisfied", "declined", "resolved"):
            raise_operation_error(
                self.request,
                f"Can't submit or edit appeal in current ({complaint_status}) complaint status",
            )

    def appeal_always(self):
        complaint = get_complaint()
        self.validate_complaint_type(complaint)
        self.validate_tender_status()
        self.validate_complaint_status(complaint)


class ComplaintAppealState(ComplaintAppealValidationsMixin, TenderState):
    def complaint_appeal_on_post(self, appeal):
        author = self.request.authenticated_role
        appeal["author"] = author
        # set author for documents passed with tender data
        for doc in appeal.get("documents", ""):
            doc["author"] = author
            assert doc["author"] in (
                "complaint_owner",
                "tender_owner",
            )
        self.validate_docs(appeal)
        self.appeal_always()

    def complaint_appeal_on_patch(self, before, after):
        self.validate_complaint_appeal_on_patch(before, after)
        self.validate_docs(after)
        self.appeal_always()

    def validate_complaint_appeal_on_patch(self, before, after):
        if self.request.authenticated_role != after["author"]:
            raise_operation_error(
                self.request,
                "Appeal can be updated only by author",
                location="url",
                name="role",
            )

        if before.get("proceeding") is not None:
            raise_operation_error(
                self.request,
                "Forbidden to patch proceeding",
                name="proceeding",
                status=422,
            )

    def validate_docs(self, data):
        for doc in data.get("documents", []):
            validate_edrpou_confidentiality_doc(doc)
