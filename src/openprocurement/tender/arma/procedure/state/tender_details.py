from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.arma.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsMixing,
)


class TenderDetailsMixing(OpenUATenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    contract_template_required = False

    working_days_config = WORKING_DAYS_CONFIG

    def on_patch(self, before, after):
        self.validate_items_classification_prefix_unchanged(before, after)
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

    @staticmethod
    def set_lot_value(tender: dict, lot: dict) -> None:
        # ARMA procedure does not have tender.value field
        pass

    @staticmethod
    def set_lot_minimal_step(tender: dict, lot: dict) -> None:
        # ARMA procedure does not have tender.minimalStep field
        pass

    def validate_lot_value(self, tender: dict, lot: dict) -> None:
        """Validate lot value.

        Validation includes lot value and lot minimal step, if required.

        :param tender: Tender dictionary
        :param lot: Lot dictionary
        :return: None
        """
        lot_value = lot.get("value", {})

        if not lot_value:
            return

        lot_value_amount = lot_value.get("amountPercentage")
        lot_min_step = lot.get("minimalStep", {})
        lot_min_step_amount_percentage = lot_min_step.get("amountPercentage")

        if lot_min_step_amount_percentage is None:
            return

        if lot_value_amount is not None and lot_value_amount < lot_min_step_amount_percentage:
            raise_operation_error(
                self.request,
                "Minimal step value should be less than lot value",
                status=422,
                name="lots",
            )

    def validate_minimal_step_limits(self, tender: dict, value_amount: float, minimal_step_amount: float) -> None:
        # ARMA procedure does not have tender.minimalStep limits
        pass

    @staticmethod
    def watch_value_meta_changes(tender):
        # ARMA procedure does not have tender.value field
        pass

    def validate_minimal_step(self, data, before=None):
        # ARMA procedure does not have tender.minimalStep field
        pass

    def validate_tender_value(self, tender):
        # ARMA procedure does not have tender.value field
        pass


class TenderDetailsState(TenderDetailsMixing, TenderState):
    pass
