from openprocurement.api.constants_env import NOTICE_DOC_REQUIRED_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.utils import tender_created_before
from openprocurement.tender.esco.constants import QUESTIONS_STAND_STILL
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState as BaseTenderDetailsState,
)


class ESCOTenderDetailsState(BaseTenderDetailsState):
    enquiry_period_timedelta = -QUESTIONS_STAND_STILL
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    def on_post(self, tender):
        super().on_post(tender)
        self.update_periods(tender)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        self.update_periods(data)

    @staticmethod
    def watch_value_meta_changes(tender):
        pass

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
            self.set_tender_lot_data(tender, lot)

    def set_tender_lot_data(self, tender, lot):
        self.set_lot_guarantee(tender, lot)
        lot["fundingKind"] = tender.get("fundingKind", "other")
        lot["minValue"] = {
            "currency": tender["minValue"]["currency"],
            "valueAddedTaxIncluded": tender["minValue"]["valueAddedTaxIncluded"],
        }

    def validate_minimal_step(self, data, before=None):
        # TODO: adjust this validation in case of it will be allowed to disable auction in esco
        # TODO: Look at original validate_minimal_step in openprocurement.tender.core.procedure.state.tender
        minimal_step_fields = ("minimalStepPercentage", "yearlyPaymentsPercentageRange")
        for field in minimal_step_fields:
            if data.get(field) is None:
                raise_operation_error(
                    self.request,
                    ["This field is required."],
                    status=422,
                    location="body",
                    name=field,
                )
