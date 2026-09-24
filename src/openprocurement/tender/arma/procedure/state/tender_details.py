from openprocurement.api.constants_env import ARMA_MIN_EXPECTED_INCOME_FROM
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.arma.constants import ARMA_TENDERING_EXTRA_PERIOD, ARMA_WORKING_DAYS_CONFIG
from openprocurement.tender.arma.procedure.models.tender import ARMAPatchTender, ARMAPostTender, ARMATender
from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.constants import AWARD_CRITERIA_RATED_CRITERIA
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.core.procedure.utils import tender_created_before


class ARMATenderDetailsMixin(TenderDetailsMixin):
    post_data_model = ARMAPostTender
    patch_data_model = ARMAPatchTender
    data_model = ARMATender

    procuring_entity_available_language_default = "uk"
    contract_template_name_allowed = False
    milestones_required = False
    milestones_delivery_financing_required = False
    award_criteria_choices = (AWARD_CRITERIA_RATED_CRITERIA,)
    award_criteria_default = AWARD_CRITERIA_RATED_CRITERIA
    tender_period_extra = ARMA_TENDERING_EXTRA_PERIOD
    vat_not_included_check = False
    working_days_config = ARMA_WORKING_DAYS_CONFIG
    tender_has_value = False

    def on_patch(self, before, after):
        self.validate_min_expected_income(before, after)
        super().on_patch(before, after)  # ARMATenderDetailsMixin.on_patch

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

    def validate_min_expected_income(self, before, after):
        if tender_created_before(ARMA_MIN_EXPECTED_INCOME_FROM, after):
            return

        before_income = self.get_lots_min_expected_income(before)
        after_income = self.get_lots_min_expected_income(after)

        if before.get("status") not in ("draft", "active.tendering") and before_income != after_income:
            raise_operation_error(
                self.request,
                "minExpectedIncome cannot be changed after tenderPeriod",
                status=422,
                name="minExpectedIncome",
            )
        if before.get("status") == "draft" and after.get("status") != "draft":
            for lot in after.get("lots") or []:
                if lot.get("status") == "cancelled":
                    continue
                if lot.get("minExpectedIncome") is None:
                    raise_operation_error(
                        self.request,
                        "minExpectedIncome is required for tender activation",
                        status=422,
                        name="minExpectedIncome",
                    )

    @staticmethod
    def get_lots_min_expected_income(tender: dict) -> dict:
        return {lot["id"]: lot.get("minExpectedIncome") for lot in tender.get("lots") or [] if lot.get("id")}


class ARMATenderDetailsState(ARMATenderDetailsMixin, ARMATenderState):
    pass
