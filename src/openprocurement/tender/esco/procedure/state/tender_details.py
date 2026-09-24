from openprocurement.api.constants_env import NOTICE_DOC_REQUIRED_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.constants import AWARD_CRITERIA_RATED_CRITERIA, EU_REQUIRED_MULTILINGUAL_FIELDS
from openprocurement.tender.core.procedure.models.auction import DecimalAuctionLotResults, DecimalAuctionResults
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.core.procedure.utils import (
    tender_created_before,
)
from openprocurement.tender.core.procedure.validation import validate_value_vat_disabled
from openprocurement.tender.esco.constants import ESCO_TENDERING_EXTRA_PERIOD
from openprocurement.tender.esco.procedure.models.tender import ESCOPatchTender, ESCOPostTender, ESCOTender


class ESCOTenderDetailsState(TenderDetailsMixin, TenderState):
    auction_results_model = DecimalAuctionResults
    auction_lot_results_model = DecimalAuctionLotResults
    award_class = Award
    post_data_model = ESCOPostTender
    patch_data_model = ESCOPatchTender
    data_model = ESCOTender

    required_multilingual_fields = EU_REQUIRED_MULTILINGUAL_FIELDS
    procuring_entity_available_language_default = "uk"
    tender_period_extra = ESCO_TENDERING_EXTRA_PERIOD
    items_delivery_required = False
    items_unit_required = False
    items_quantity_required = False
    items_classification_id_check_on_post = False
    milestones_required = False
    milestones_delivery_financing_required = False
    features_max_weight = 0.25
    award_criteria_choices = (AWARD_CRITERIA_RATED_CRITERIA,)
    award_criteria_default = AWARD_CRITERIA_RATED_CRITERIA
    minimal_step_fields = ("minimalStepPercentage", "yearlyPaymentsPercentageRange")

    def on_post(self, tender):
        super().on_post(tender)
        self.update_periods(tender)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        self.update_periods(data)

    def update_periods(self, tender):
        self.update_complaint_period(tender)
        # TODO: remove these lines after NOTICE_DOC_REQUIRED_FROM will be set on prod and some time passes
        if (
            tender_created_before(NOTICE_DOC_REQUIRED_FROM)
            and tender["status"] == "active.tendering"
            and not tender.get("noticePublicationDate")
        ):
            tender["noticePublicationDate"] = get_request_now().isoformat()

    def validate_tender_value(self, tender):
        """Validate tender minValue.

        Validation includes tender minValue.

        :param tender: Tender dictionary
        :return: None
        """
        has_value_estimation = tender["config"]["hasValueEstimation"]
        tender_min_value = tender.get("minValue", {})

        if not tender_min_value:
            return

        tender_min_value_amount = tender_min_value.get("amount")
        if has_value_estimation is True and tender_min_value_amount is None:
            raise_operation_error(
                self.request,
                "This field is required",
                status=422,
                location="body",
                name="minValue.amount",
            )

        if has_value_estimation is False and tender_min_value_amount:
            raise_operation_error(
                self.request,
                "Rogue field",
                status=422,
                location="body",
                name="minValue.amount",
            )

        # CS-21518 - for ESCO tenders we need to validate that minValue has valueAddedTaxIncluded False
        if self.vat_not_included_check:
            validate_value_vat_disabled(
                self.request, tender_min_value, "minValue", self.vat_not_included_validation_from
            )

    def validate_tender_lots(self, tender: dict, before=None) -> None:
        """Validate lot minValue.

        Validation includes lot minValue.

        :param tender: Tender dictionary
        :param lot: Lot dictionary
        :return: None
        """
        has_value_estimation = tender["config"]["hasValueEstimation"]

        for lot in tender.get("lots", {}):
            lot_min_value = lot.get("minValue", {})

            if not lot_min_value:
                return

            lot_value_amount = lot_min_value.get("amount")

            if has_value_estimation is True and lot_value_amount is None:
                raise_operation_error(
                    self.request,
                    "This field is required",
                    status=422,
                    name="lots.minValue.amount",
                )

            if has_value_estimation is False and lot_value_amount:
                raise_operation_error(
                    self.request,
                    "Rogue field",
                    status=422,
                    name="lots.minValue.amount",
                )

            # CS-21518 - for ESCO tenders we need to validate that lot minValue has valueAddedTaxIncluded False
            if self.vat_not_included_check:
                validate_value_vat_disabled(
                    self.request, lot_min_value, "lots.minValue", self.vat_not_included_validation_from
                )

            self.set_tender_lot_data(tender, lot)
            self.validate_lot_minimal_step(lot, before)

    def set_tender_lot_data(self, tender, lot):
        self.set_lot_guarantee(tender, lot)
        lot["fundingKind"] = tender.get("fundingKind", "other")
        lot["minValue"] = {
            "currency": tender["minValue"]["currency"],
            "valueAddedTaxIncluded": tender["minValue"]["valueAddedTaxIncluded"],
        }
