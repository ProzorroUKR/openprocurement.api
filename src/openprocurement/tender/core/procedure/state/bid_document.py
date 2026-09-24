from copy import deepcopy

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_bid
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.state.utils import invalidate_pending_bid
from openprocurement.tender.core.procedure.validation import OPERATIONS, validate_doc_type_quantity


class BidDocumentState(BaseDocumentState):
    document_owner_item_name = "bid"
    # financial / qualification documents of a bid are hidden (except from the owner) in more statuses
    bid_document_restricted_view = False
    # tender statuses in which bid documents can be added / updated (cfaua: also qualification.stand-still)
    bid_document_allowed_tender_statuses: tuple = ("active.tendering", "active.qualification", "active.awarded")

    check_edrpou_confidentiality = False
    allow_deletion = True

    def validate_document_view_allowed(self):
        request, tender, bid = self.request, get_tender(), self.request.validated["bid"]
        if self.is_item_owner("bid"):
            return
        if self.bid_document_restricted_view:
            forbidden_tender_statuses = (
                "active.tendering",
                "active.pre-qualification",
                "active.pre-qualification.stand-still",
                "active.auction",
            )
            forbidden_bid_statuses = ("invalid", "deleted", "invalid.pre-qualification", "unsuccessful")
        else:
            if tender["config"].get("hasPrequalification"):
                forbidden_tender_statuses = ("active.tendering",)
            else:
                forbidden_tender_statuses = ("active.tendering", "active.auction")
            forbidden_bid_statuses = ("invalid", "deleted")
        if tender["status"] in forbidden_tender_statuses:
            raise_operation_error(request, f"Can't view bid documents in current ({tender['status']}) tender status")
        if bid["status"] in forbidden_bid_statuses:
            raise_operation_error(request, f"Can't view bid documents in current ({bid['status']}) bid status")

    def validate_document_operation_allowed(self):
        request, tender, bid = self.request, get_tender(), self.request.validated["bid"]
        operation = OPERATIONS.get(request.method)
        if not self.bid_document_allowed_by_qualification_milestone():
            if tender["status"] not in self.bid_document_allowed_tender_statuses:
                raise_operation_error(
                    request, f"Can't {operation} document in current ({tender['status']}) tender status"
                )
            allowed_award_statuses = ("active",)
            if tender["status"] in ("active.qualification", "active.awarded") and not any(
                award["status"] in allowed_award_statuses and award["bid_id"] == bid["id"]
                for award in tender.get("awards", "")
            ):
                raise_operation_error(
                    request,
                    f"Can't {operation} document because award of bid is not in one of statuses {allowed_award_statuses}",
                )
        if tender["status"] == "active.tendering":
            tender_period = tender["tenderPeriod"]
            now = get_request_now().isoformat()
            if tender_period.get("startDate") and now < tender_period["startDate"] or now > tender_period["endDate"]:
                raise_operation_error(
                    request,
                    "Document can be {} only during the tendering period: from ({}) to ({}).".format(
                        "added" if request.method == "POST" else "updated",
                        tender_period.get("startDate"),
                        tender_period["endDate"],
                    ),
                )
        if bid["status"] in ("unsuccessful", "deleted"):
            raise_operation_error(request, f"Can't {operation} document at '{bid['status']}' bid status")

    def bid_document_allowed_by_qualification_milestone(self):
        """An active 24 hours / low price milestone of the pending award (qualification) of the bid
        allows to add / update the bid documents"""
        now = get_request_now().isoformat()
        tender = get_tender()
        bid_id = self.request.validated["bid"]["id"]
        awards = [q for q in tender.get("awards", "") if q["status"] == "pending" and q["bid_id"] == bid_id]
        if "qualifications" in tender:  # for procedures with pre-qualification
            qualifications = [q for q in tender["qualifications"] if q["status"] == "pending" and q["bidID"] == bid_id]
        else:
            qualifications = awards
        for q in qualifications:
            for milestone in q.get("milestones", ""):
                if milestone["code"] == "24h" and milestone["date"] <= now <= milestone["dueDate"]:
                    return True
        for award in awards:
            for milestone in award.get("milestones", ""):
                if milestone["code"] == "alp" and milestone["date"] <= now <= milestone["dueDate"]:
                    return True
        return False

    def validate_sign_documents_already_exists(self, doc_data, doc_envelope):
        bid_docs = deepcopy(get_bid().get(doc_envelope, []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            bid_docs.extend(new_documents)
        else:  # PATCH/PUT
            bid_docs.append(doc_data)
        validate_doc_type_quantity(bid_docs, document_type="proposal", obj_name="bid")

    def validate_document_post(self, data):
        super().validate_document_post(data)
        if self.request.method == "PUT":  # new version of an existing document
            self.validate_confidentiality_change(self.request.validated["document"], data)

    def validate_document_patch(self, before, after):
        super().validate_document_patch(before, after)
        self.validate_confidentiality_change(before, after)

    def validate_confidentiality_change(self, before, after):
        tender_status = get_tender()["status"]
        if tender_status != "active.tendering" and before.get("confidentiality", "public") != after.get(
            "confidentiality", "public"
        ):
            raise_operation_error(
                self.request,
                f"Can't update document confidentiality in current ({tender_status}) tender status",
            )

    def document_always(self, data):
        super().document_always(data)
        invalidate_pending_bid()


class BidFinancialDocumentState(BidDocumentState):
    """financialDocuments / qualificationDocuments of a bid"""

    bid_document_restricted_view = True
