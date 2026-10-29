from hashlib import sha512

from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.api.validation import (
    validate_accreditation_level_owner,
    validate_json_data,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)
from openprocurement.tender.open.procedure.state.tender_details import (
    AboveThresholdEUTenderDetailsState,
    AboveThresholdTenderDetailsState,
    AboveThresholdUATenderDetailsState,
    BelowThresholdTenderDetailsState,
    DefenseTenderDetailsState,
    SimpleDefenseTenderDetailsState,
)


class OwnershipState(BaseState):
    """Change of the object owner by a transfer (POST /<objects>/{id}/ownership)"""

    # the object of the ownership change (request.validated key)
    ownership_item_name: str
    ownership_transfer_accreditations: tuple = ()

    # --- request validation (called from the views) ---

    def validate_ownership_post_request(self):
        self.validate_ownership_transfer_accreditation()
        self.validate_ownership_owner_accreditation()
        self.validate_ownership_data()
        self.validate_ownership_item_status()
        self.validate_ownership_transfer_token()

    def get_ownership_transfer_accreditations(self):
        return self.ownership_transfer_accreditations, None

    def validate_ownership_transfer_accreditation(self):
        levels, kind_central_levels = self.get_ownership_transfer_accreditations()
        self.validate_accreditation_level(
            levels=levels,
            item="ownership",
            operation="change",
            source=self.ownership_item_name,
            kind_central_levels=kind_central_levels,
        )

    def validate_ownership_owner_accreditation(self):
        """the broker of the current owner may hand over the object"""
        owner = self.request.validated[self.ownership_item_name]["owner"]
        validate_accreditation_level_owner(self.request, owner, "ownership", "ownership", "change")

    def validate_ownership_data(self):
        data = validate_json_data(self.request)
        for field in ("id", "transfer"):
            if not data.get(field):
                self.request.errors.add("body", field, "This field is required.")
        if self.request.errors:
            self.request.errors.status = 422
            raise error_handler(self.request)
        self.request.validated["ownership_data"] = data

    def is_ownership_item_status_allowed(self, status):
        raise NotImplementedError

    def validate_ownership_item_status(self):
        status = self.request.validated[self.ownership_item_name]["status"]
        if not self.is_ownership_item_status_allowed(status):
            raise_operation_error(
                self.request,
                f"Can't update credentials in current ({status}) {self.ownership_item_name} status",
            )

    def validate_ownership_transfer_token(self):
        token = self.request.validated["ownership_data"]["transfer"]
        transfer_token = self.request.validated[self.ownership_item_name]["transfer_token"]
        if transfer_token != sha512(token.encode("utf-8")).hexdigest():
            raise_operation_error(self.request, "Invalid transfer", name="transfer")


class TenderOwnershipState(OwnershipState):
    ownership_item_name = "tender"
    # the tender details state of the procedure holds the transfer accreditations
    ownership_tender_states: dict = {
        "belowThreshold": BelowThresholdTenderDetailsState,
        "aboveThreshold": AboveThresholdTenderDetailsState,
        "aboveThresholdUA": AboveThresholdUATenderDetailsState,
        "aboveThresholdEU": AboveThresholdEUTenderDetailsState,
        "negotiation": NegotiationTenderDetailsState,
        "negotiation.quick": NegotiationTenderDetailsState,
        "aboveThresholdUA.defense": DefenseTenderDetailsState,
        "competitiveDialogueUA": CDStage1UATenderDetailsState,
        "competitiveDialogueEU": CDStage1EUTenderDetailsState,
        "competitiveDialogueUA.stage2": CDStage2UATenderDetailsState,
        "competitiveDialogueEU.stage2": CDStage2EUTenderDetailsState,
        "reporting": ReportingTenderDetailsState,
        "esco": ESCOTenderDetailsState,
        "closeFrameworkAgreementUA": CFAUATenderDetailsState,
        "closeFrameworkAgreementSelectionUA": CFASelectionTenderDetailsState,
        "priceQuotation": None,
        "simple.defense": SimpleDefenseTenderDetailsState,
    }
    ownership_not_allowed_statuses = (
        "complete",
        "unsuccessful",
        "cancelled",
        "active.stage2.waiting",
        "draft.pending",
        "draft.unsuccessful",
    )

    def get_ownership_transfer_accreditations(self):
        state = self.ownership_tender_states.get(self.request.validated["tender"]["procurementMethodType"])
        if state is None:
            raise NotImplementedError()
        if hasattr(state, "tender_transfer_accreditations"):
            levels = state.tender_transfer_accreditations
        elif hasattr(state, "tender_create_accreditations"):
            levels = state.tender_create_accreditations
        else:
            raise NotImplementedError()
        return levels, getattr(state, "tender_central_accreditations", None)

    def is_ownership_item_status_allowed(self, status):
        return status not in self.ownership_not_allowed_statuses


class PlanOwnershipState(OwnershipState):
    ownership_item_name = "plan"
    ownership_transfer_accreditations = (
        AccreditationLevel.ACCR_1,
        AccreditationLevel.ACCR_3,
        AccreditationLevel.ACCR_5,
    )

    def is_ownership_item_status_allowed(self, status):
        return status == "scheduled"


class ContractOwnershipState(OwnershipState):
    ownership_item_name = "contract"
    ownership_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    def is_ownership_item_status_allowed(self, status):
        return status in ("pending", "active")


class AgreementOwnershipState(OwnershipState):
    ownership_item_name = "agreement"
    ownership_transfer_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    def is_ownership_item_status_allowed(self, status):
        return status == "active"
