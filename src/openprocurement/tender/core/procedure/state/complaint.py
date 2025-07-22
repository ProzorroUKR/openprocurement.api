from logging import getLogger

from openprocurement.api.constants_env import OBJECTIONS_ADDITIONAL_VALIDATION_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_agreement, get_tender
from openprocurement.api.utils import get_uah_amount_from_value, raise_operation_error
from openprocurement.api.validation import validate_json_data
from openprocurement.tender.core.constants import (
    COMPLAINT_AMOUNT_RATE,
    COMPLAINT_ENHANCED_AMOUNT_RATE,
    COMPLAINT_ENHANCED_MAX_AMOUNT,
    COMPLAINT_ENHANCED_MIN_AMOUNT,
    COMPLAINT_MAX_AMOUNT,
    COMPLAINT_MIN_AMOUNT,
)
from openprocurement.tender.core.procedure.models.complaint import (
    AdministratorPatchComplaint,
    BotPatchComplaint,
    CancellationPatchComplaint,
    DraftPatchComplaint,
    ReviewPatchComplaint,
    TendererActionPatchComplaint,
    TendererResolvePatchComplaint,
)
from openprocurement.tender.core.procedure.models.complaint_objection import (
    ObjectionRelatesTo,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    find_item_by_id,
    get_supplier_contract,
    restrict_value_to_bounds,
    round_up_to_ten,
    tender_created_after,
    tender_created_after_2020_rules,
)
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)

LOGGER = getLogger(__name__)


class BaseComplaintStateMixin:
    def validate_add_complaint_with_tender_cancellation_in_pending(self, tender):
        if tender_created_after_2020_rules():
            if any(i.get("status") == "pending" and not i.get("relatedLot") for i in tender.get("cancellations", "")):
                raise_operation_error(
                    self.request,
                    "Can't add complaint if tender have cancellation in pending status",
                )


class ComplaintStateMixin(BaseComplaintStateMixin):
    create_allowed_tender_statuses = ("active.tendering",)
    update_allowed_tender_statuses = ("active.tendering",)
    draft_patch_model = DraftPatchComplaint
    complaints_configuration = "hasTenderComplaints"
    all_documents_should_be_public = False
    should_validate_complaint_author_qualified_supplier = False

    # POST
    def validate_complaint_on_post(self, complaint):
        tender = get_tender()
        self.validate_complaint_config()
        self.validate_create_allowed_tender_status()
        self.validate_lot_status()
        self.validate_complaint_author(complaint)
        self.validate_objections(complaint)
        self.validate_tender_in_complaint_period(tender)

        self.validate_add_complaint_with_tender_cancellation_in_pending(tender)
        self.validate_add_complaint_with_lot_cancellation_in_pending(tender, complaint)
        self.validate_docs(complaint)

    def complaint_on_post(self, complaint):
        tender = get_tender()
        if tender_created_after_2020_rules():
            amount = self.get_complaint_amount(tender, complaint)
            complaint["value"] = {"amount": round_up_to_ten(amount), "currency": "UAH"}

        for doc in complaint.get("documents", ""):
            doc["author"] = "complaint_owner"

        self.always(tender)

    def validate_complaint_config(self):
        tender = get_tender()
        if tender["config"][self.complaints_configuration] is False:
            raise_operation_error(
                self.request,
                "Can't add complaint as it is forbidden by configuration",
            )

    def validate_create_allowed_tender_status(self):
        if self.create_allowed_tender_statuses:
            tender = get_tender()
            if tender["status"] not in self.create_allowed_tender_statuses:
                raise_operation_error(
                    self.request,
                    f"Can't add complaint in current ({tender['status']}) tender status",
                )

    def validate_update_allowed_tender_status(self):
        if self.update_allowed_tender_statuses:
            tender = get_tender()
            if tender["status"] not in self.update_allowed_tender_statuses:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint in current ({tender['status']}) tender status",
                )

    def validate_docs(self, data):
        for doc in data.get("documents", []):
            validate_edrpou_confidentiality_doc(doc, should_be_public=self.all_documents_should_be_public)
            if doc["documentOf"] == "post":
                if not any(i and doc.get("relatedItem") == i["id"] for i in data.get("posts", "")):
                    raise_operation_error(
                        self.request,
                        "relatedItem should be one of complaint posts",
                        status=422,
                        name="relatedItem",
                    )
            elif self.request.authenticated_role != "aboveThresholdReviewers" and data["status"] == "pending":
                raise_operation_error(
                    self.request,
                    f"Can submit or edit document not related to post in current ({data['status']}) complaint "
                    f"status for {self.request.authenticated_role}",
                )

    # PATCH
    def validate_complaint_on_patch(self, before, complaint):
        # validate forbidden for update fields
        for k in ("id", "scheme", "legalName"):
            if before["author"]["identifier"][k] != complaint["author"]["identifier"][k]:
                raise_operation_error(
                    self.request,
                    f"Can't change complaint author {k}",
                )
        self.validate_lot_status()

        # auth role action scenario
        _, handler = self.get_patch_action_model_and_handler()
        handler(complaint)
        self.validate_objections(complaint)

    def get_patch_data_model(self):
        model, _ = self.get_patch_action_model_and_handler()
        return model

    def get_patch_action_model_and_handler(self):
        request = self.request
        tender = get_tender()
        new_rules = tender_created_after_2020_rules()
        auth_role = request.authenticated_role
        current_complaint = request.validated["complaint"]
        status = current_complaint["status"]
        request_data = validate_json_data(request)
        new_status = request_data.get("status") or status

        self.validate_update_allowed_tender_status()

        def empty_handler(_):
            pass

        if auth_role == "bots":
            if new_rules and status == "draft" and new_status in ("pending", "mistaken"):
                if new_status == "mistaken":

                    def handler(complaint):
                        complaint["rejectReason"] = "incorrectPayment"

                    return BotPatchComplaint, handler
                elif new_status == "pending":

                    def handler(complaint):
                        complaint["dateSubmitted"] = get_request_now().isoformat()

                    return BotPatchComplaint, handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status",
                )
        elif auth_role == "complaint_owner":
            if new_status == "cancelled" and status == "draft" and not new_rules:

                def handler(complaint):
                    complaint["dateCanceled"] = get_request_now().isoformat()

                return CancellationPatchComplaint, handler
            elif new_rules and status == "draft" and new_status == "mistaken":

                def handler(complaint):
                    complaint["rejectReason"] = "cancelledByComplainant"

                return self.draft_patch_model, handler
            elif status in ["pending", "accepted"] and new_status == "stopping" and not new_rules:

                def handler(complaint):
                    complaint["dateCanceled"] = get_request_now().isoformat()

                return CancellationPatchComplaint, handler
            elif status == "draft" and new_status == status:
                return self.draft_patch_model, empty_handler
            elif (
                tender["status"] == "active.tendering"
                and status == "draft"
                and new_status == "pending"
                and not new_rules
            ):

                def handler(complaint):
                    self.validate_tender_in_complaint_period(tender)
                    complaint["dateSubmitted"] = get_request_now().isoformat()

                return self.draft_patch_model, handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status",
                )

        elif auth_role == "tender_owner":
            if status == "satisfied" and new_status == status:
                return TendererResolvePatchComplaint, empty_handler
            elif (
                status == "satisfied"
                and request_data.get("tendererAction", current_complaint.get("tendererAction"))
                and new_status == "resolved"
            ):

                def handler(complaint):
                    complaint["status"] = "resolved"
                    complaint["tendererActionDate"] = get_request_now().isoformat()

                return TendererResolvePatchComplaint, handler
            elif status in ["pending", "accepted"]:
                return TendererActionPatchComplaint, empty_handler
            else:
                raise_operation_error(self.request, "Forbidden")

        elif auth_role == "aboveThresholdReviewers":
            if status in ["pending", "accepted", "stopping"] and new_status == status:
                return ReviewPatchComplaint, empty_handler
            elif status in ["pending", "stopping"] and (
                (not new_rules and new_status in ["invalid", "mistaken"]) or (new_status == "invalid")
            ):

                def handler(complaint):
                    complaint["dateDecision"] = get_request_now().isoformat()
                    complaint["acceptance"] = False

                return ReviewPatchComplaint, handler
            elif status == "pending" and new_status == "accepted":

                def handler(complaint):
                    complaint["dateAccepted"] = get_request_now().isoformat()
                    complaint["acceptance"] = True

                return ReviewPatchComplaint, handler
            elif status in ["accepted", "stopping"] and new_status == "declined":
                return ReviewPatchComplaint, self.reviewers_declined_handler
            elif status in ["accepted", "stopping"] and new_status == "satisfied":
                return ReviewPatchComplaint, self.reviewers_satisfied_handler
            elif (
                (not new_rules and status in ["pending", "accepted", "stopping"])
                or (new_rules and status == "accepted")
                and new_status == "stopped"
            ):

                def handler(complaint):
                    complaint["dateDecision"] = get_request_now().isoformat()
                    complaint["dateCanceled"] = complaint.get("dateCanceled") or get_request_now().isoformat()

                return ReviewPatchComplaint, handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status",
                )
        elif auth_role == "Administrator":
            return AdministratorPatchComplaint, empty_handler
        else:
            raise_operation_error(request, f"Cannot perform any action on complaint as {auth_role}")

    def reviewers_satisfied_handler(self, complaint):
        complaint["dateDecision"] = get_request_now().isoformat()

    def reviewers_declined_handler(self, complaint):
        complaint["dateDecision"] = get_request_now().isoformat()

    def complaint_on_patch(self, before, complaint):
        if before["status"] != complaint["status"]:
            self.complaint_status_up(before["status"], complaint["status"], complaint)

        self.always(get_tender())

    def complaint_status_up(self, before, after, complaint):
        complaint["date"] = get_request_now().isoformat()
        # if before != "pending" and after != "cancelled":
        #     raise_operation_error(self.request, "Can't update qualification status")

    def validate_tender_in_complaint_period(self, tender):
        if tender.get("complaintPeriod") and get_request_now() > dt_from_iso(tender["complaintPeriod"]["endDate"]):
            raise_operation_error(
                self.request,
                "Can submit complaint not later than complaintPeriod end date",
            )

    def validate_lot_status(self):
        pass

    def get_related_lot_obj(self, tender, complaint):
        if related_lot := complaint.get("relatedLot"):
            for lot in tender.get("lots"):
                if lot["id"] == related_lot:
                    return lot

    def get_complaint_amount(self, tender, complaint):
        related_lot = self.get_related_lot_obj(tender, complaint)
        value = related_lot["value"] if related_lot else tender["value"]
        base_amount = get_uah_amount_from_value(self.request, value, {"complaint_id": complaint["id"]})
        if tender["status"] == "active.tendering":
            amount = restrict_value_to_bounds(
                base_amount * COMPLAINT_AMOUNT_RATE,
                COMPLAINT_MIN_AMOUNT,
                COMPLAINT_MAX_AMOUNT,
            )
        else:
            amount = restrict_value_to_bounds(
                base_amount * COMPLAINT_ENHANCED_AMOUNT_RATE,
                COMPLAINT_ENHANCED_MIN_AMOUNT,
                COMPLAINT_ENHANCED_MAX_AMOUNT,
            )
        return amount

    def validate_add_complaint_with_lot_cancellation_in_pending(self, tender, complaint):
        if tender_created_after_2020_rules():
            lot = self.get_related_lot_obj(tender, complaint)
            if lot:
                if any(
                    i.get("status") == "pending" and i.get("relatedLot") == lot["id"]
                    for i in tender.get("cancellations", "")
                ):
                    raise_operation_error(
                        self.request,
                        "Can't add complaint with 'pending' lot cancellation",
                    )

    def validate_objections(self, complaint):
        if tender_created_after(OBJECTIONS_ADDITIONAL_VALIDATION_FROM):
            for objection in complaint.get("objections", []):
                if objection.get("sequenceNumber") is None:
                    raise_operation_error(
                        self.request,
                        "sequenceNumber field is required",
                        status=422,
                        name="objections",
                    )
                if len(objection.get("arguments", [])) > 1:
                    raise_operation_error(
                        self.request,
                        "Can't add more than 1 argument for objection",
                        status=422,
                    )
        self.validate_objection_related_item(complaint)

    def validate_objection_related_item(self, complaint):
        if complaint.get("status", "draft") == "draft" and (objections := complaint.get("objections", [])):
            tender = get_tender()
            for objection in objections:
                relates_to = objection["relatesTo"]
                related_item = objection["relatedItem"]
                if relates_to == ObjectionRelatesTo.tender.value:
                    if related_item != tender.get("_id"):
                        raise_operation_error(
                            self.request,
                            "Invalid tender id",
                            status=422,
                            name="objections.relatedItem",
                        )
                else:
                    items = tender.get(f"{relates_to}s", [])
                    obj = find_item_by_id(items, related_item)
                    if not obj:
                        raise_operation_error(
                            self.request,
                            f"Invalid {relates_to} id",
                            status=422,
                            name="objections.relatedItem",
                        )
                    if relates_to in ("award", "qualification") and obj.get("status") not in ("active", "unsuccessful"):
                        raise_operation_error(
                            self.request,
                            f"Relate objection to {relates_to} in {obj.get('status')} is forbidden",
                            status=422,
                            name="objections.relatedItem",
                        )

    def validate_complaint_author(self, complaint):
        if not self.should_validate_complaint_author_qualified_supplier:
            return

        tender = get_tender()
        if not tender["config"]["hasPreSelectionAgreement"]:
            return

        agreement = get_agreement()
        if not agreement:
            return

        supplier_contract = get_supplier_contract(
            agreement["contracts"],
            [complaint["author"]],
        )
        if not supplier_contract:
            raise_operation_error(self.request, "Forbidden to add complaint for non-qualified suppliers")


class TenderComplaintState(ComplaintStateMixin, TenderState):
    def validate_objection_related_item(self, complaint):
        super().validate_objection_related_item(complaint)
        if objections := complaint.get("objections", []):
            related_lot = complaint.get("relatedLot")
            for objection in objections:
                if objection["relatesTo"] == ObjectionRelatesTo.lot.value:
                    if not related_lot or objection["relatedItem"] != related_lot:
                        raise_operation_error(
                            self.request,
                            "Complaint's objection must relate to the same lot id as mentioned in complaint's relatedLot",
                            status=422,
                            name="objections.relatedItem",
                        )
                elif related_lot:
                    raise_operation_error(
                        self.request,
                        f"Complaint's objection must not relate to {objection['relatesTo']} if relatedLot mentioned",
                        status=422,
                        name="objections.relatedItem",
                    )
