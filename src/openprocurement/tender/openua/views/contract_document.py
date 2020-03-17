# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.contract_document import TenderAwardContractDocumentResource


@optendersresource(
    name="aboveThresholdUA:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender contract documents",
)
class TenderUaAwardContractDocumentResource(TenderAwardContractDocumentResource):
    def validate_contract_document(self, operation):
        """ TODO move validators
        This class is inherited from below package, but validate_contract_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.validated["tender_status"] not in ["active.qualification", "active.awarded"]:
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
                if i.id
                in [
                    a.lotID
                    for a in self.request.validated["tender"].awards
                    if a.id == self.request.validated["contract"].awardID
                ]
            ]
        ):
            raise_operation_error(self.request, "Can {} document only in active lot status".format(operation))
        if self.request.validated["contract"].status not in ["pending", "pending.winnerSigning", "active"]:
            raise_operation_error(self.request, "Can't {} document in current contract status".format(operation))
        if any(
            [
                any([c.status == "accepted" for c in i.complaints])
                for i in self.request.validated["tender"].awards
                if i.lotID
                in [
                    a.lotID
                    for a in self.request.validated["tender"].awards
                    if a.id == self.request.validated["contract"].awardID
                ]
            ]
        ):
            raise_operation_error(self.request, "Can't {} document with accepted complaint")
        return True
