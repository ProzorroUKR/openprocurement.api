# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint_document import TenderUaAwardComplaintDocumentResource
from openprocurement.tender.openua.constants import STATUS4ROLE


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender award complaint documents",
)
class TenderEUAwardComplaintDocumentResource(TenderUaAwardComplaintDocumentResource):
    def validate_complaint_document(self, operation):
        """ TODO move validators
        This class is inherited in limited and openeu (qualification complaint) package,
        but validate_complaint_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if operation == "update" and self.request.authenticated_role != self.context.author:
            self.request.errors.add("url", "role", "Can update document only author")
            self.request.errors.status = 403
            raise error_handler(self.request)
        if self.request.validated["tender_status"] not in tuple(
            ["active.qualification.stand-still", "active.qualification"]
        ):
            raise_operation_error(
                self.request,
                "Can't {} document in current ({}) tender status".format(
                    operation, self.request.validated["tender_status"]
                ),
            )
        if any(
            [
                i.status != "active"
                for i in self.request.validated["tender"].lots
                if i.id == self.request.validated["award"].lotID
            ]
        ):
            raise_operation_error(self.request, "Can {} document only in active lot status".format(operation))
        if self.request.validated[
            "complaint"
        ].status not in STATUS4ROLE.get(
            self.request.authenticated_role, []
        ):
            raise_operation_error(
                self.request,
                "Can't {} document in current ({}) complaint status".format(
                    operation, self.request.validated["complaint"].status
                ),
            )
        return True
