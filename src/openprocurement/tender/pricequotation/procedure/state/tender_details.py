from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class TenderDetailsState(TenderDetailsMixing, PriceQuotationTenderState):
    tender_create_accreditations = (ACCR_1, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_2,)
    should_initialize_enquiry_period = False
    should_validate_pre_selection_agreement = True
    should_validate_cpv_prefix = False
    should_validate_notice_doc_required = True
    agreement_field = "agreement"
    should_validate_related_lot_in_items = False
    agreement_allowed_types = [
        DPS_TYPE,
        ELECTRONIC_CATALOGUE_TYPE,
    ]
    agreement_without_items_forbidden = False
    agreement_min_active_contracts = 3
    should_match_agreement_procuring_entity = True
    items_profile_required = False

    contract_template_required = True
    contract_template_name_patch_statuses = ("draft",)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

        if before == "draft" and after == "active.tendering":
            data["tenderPeriod"]["startDate"] = get_request_now().isoformat()

        if after in self.unsuccessful_statuses:
            self.set_contracts_cancelled(after)

    def validate_tender_period_extension(self, tender):
        pass

    @staticmethod
    def set_enquiry_period_invalidation_date(tender):
        pass

    def invalidate_bids_data(self, tender):
        pass


class CatalogueTenderDetailsState(TenderDetailsState):
    agreement_min_active_contracts = 1
    should_match_agreement_procuring_entity = False
    should_validate_profiles_agreement_id = True
    items_profile_required = True


class DPSTenderDetailsState(TenderDetailsState):
    agreement_without_items_forbidden = True

    @property
    def should_match_agreement_procuring_entity(self):
        if (
            get_object("tender")["procuringEntity"]["kind"] == ProcuringEntityKind.DEFENSE
            and get_object("agreement")["procuringEntity"]["kind"] == ProcuringEntityKind.DEFENSE
        ):
            # Defense procuring entity can use agreement with other defense procuring entity
            return False

        return True
