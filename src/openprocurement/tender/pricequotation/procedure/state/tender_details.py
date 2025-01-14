from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5
from openprocurement.api.constants import CONTRACT_TEMPLATES_KEYS
from openprocurement.api.context import get_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.pricequotation.constants import DEFAULT_TEMPLATE_KEY
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
    items_profile_required = False
    agreement_min_active_contracts = 3
    should_match_agreement_procuring_entity = True

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

        if before == "draft" and after == "active.tendering":
            data["tenderPeriod"]["startDate"] = get_now().isoformat()

        # TODO: it's insurance for some period while refusing PQ bot, just to have opportunity manually activate tender
        if before == "draft.publishing" and after == "active.tendering":
            self.validate_pre_selection_agreement(data)
            self.validate_pre_selection_agreement_on_activation(data)
            data["tenderPeriod"]["startDate"] = get_now().isoformat()

        if before == "draft.unsuccessful" and after != before:
            raise_operation_error(
                get_request(),
                f"Can't change status from {before} to {after}",
            )

        if after == "active.tendering" and after != before:
            self.set_contract_template_name(data)

        if after in self.unsuccessful_statuses:
            self.set_contracts_cancelled(after)

    def set_contract_template_name(self, data):
        DEFAULT_TEMPLATE_CLASSIFICATION_PREFIX_LENGTH = 4
        CUSTOM_LENGTH_TEMPLATE_CLASSIFICATION_PREFIXES = ("15", "336")
        EXCLUDED_TEMPLATE_CLASSIFICATION_PREFIXES = ("0931",)

        items = data.get("items")
        if not items or any(i.get("documentType", "") == "contractProforma" for i in data.get("documents", "")):
            return

        classification_id = items[0].get("classification", {}).get("id")
        template_name = None
        if not classification_id:
            return

        if any(classification_id.startswith(prefix) for prefix in CUSTOM_LENGTH_TEMPLATE_CLASSIFICATION_PREFIXES):
            for prefix in CUSTOM_LENGTH_TEMPLATE_CLASSIFICATION_PREFIXES:
                if classification_id.startswith(prefix):
                    classification_prefix = classification_id[: len(prefix)]
                    break
        else:
            classification_prefix = classification_id[:DEFAULT_TEMPLATE_CLASSIFICATION_PREFIX_LENGTH]

        if classification_prefix not in EXCLUDED_TEMPLATE_CLASSIFICATION_PREFIXES:
            for key in CONTRACT_TEMPLATES_KEYS:
                if key.startswith(classification_prefix):
                    template_name = key
                    break
                elif key.startswith(DEFAULT_TEMPLATE_KEY):
                    template_name = key

        if template_name:
            data["contractTemplateName"] = template_name

    def validate_tender_period_extension(self, tender):
        pass

    @staticmethod
    def set_enquiry_period_invalidation_date(tender):
        pass

    def invalidate_bids_data(self, tender):
        pass


class CatalogueTenderDetailsState(TenderDetailsState):
    items_profile_required = True
    agreement_min_active_contracts = 1
    should_match_agreement_procuring_entity = False


class DPSTenderDetailsState(TenderDetailsState):
    agreement_without_items_forbidden = True
