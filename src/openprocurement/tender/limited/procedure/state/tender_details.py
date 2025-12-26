from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.constants import CAUSE_DETAILS_MAPPING
from openprocurement.api.constants_env import (
    CAUSE_DETAILS_REQUIRED_FROM,
    QUICK_CAUSE_REQUIRED_FROM,
)
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.core.procedure.utils import (
    tender_created_after,
    tender_created_before,
)
from openprocurement.tender.limited.constants import WORKING_DAYS_CONFIG
from openprocurement.tender.limited.procedure.models.tender import (
    reporting_cause_is_required,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class CauseDetailsMixing:
    def validate_cause_required(self, data):
        if tender_created_after(CAUSE_DETAILS_REQUIRED_FROM):
            if not data.get("causeDetails"):
                if data.get("procurementMethodType") == "reporting" and not reporting_cause_is_required(data):
                    pass
                else:
                    raise_operation_error(
                        self.request,
                        "This field is required.",
                        status=422,
                        location="body",
                        name="causeDetails",
                    )
            for field_name in ("cause", "causeDescription", "causeDescription_en", "causeDescription_ru"):
                if data.get(field_name):
                    raise_operation_error(
                        self.request,
                        "Rogue field.",
                        status=422,
                        location="body",
                        name=field_name,
                    )
        else:
            if not data.get("cause") and not data.get("causeDetails"):
                if data.get("procurementMethodType") == "reporting" and not reporting_cause_is_required(data):
                    pass
                elif data.get("procurementMethodType") == "negotiation.quick" and tender_created_before(
                    QUICK_CAUSE_REQUIRED_FROM
                ):
                    pass
                else:
                    raise_operation_error(
                        self.request,
                        "This field is required.",
                        status=422,
                        location="body",
                        name="cause",
                    )
            for field_name, field_alt_name in [
                ("cause", "code"),
                ("causeDescription", "description"),
                ("causeDescription_en", "description_en"),
            ]:
                if (
                    data.get(field_name)
                    and data.get("causeDetails", {}).get(field_alt_name)
                    and data[field_name] != data["causeDetails"][field_alt_name]
                ):
                    raise_operation_error(
                        self.request,
                        f"Fields should be equal: {field_name} and causeDetails.{field_alt_name}.",
                        status=422,
                        location="body",
                        name=field_name,
                    )

    def set_cause_details_data(self, data):
        if cause_details := data.get("causeDetails"):
            procurement_method_type = data["procurementMethodType"]
            if cause_details.get("code") not in CAUSE_DETAILS_MAPPING[procurement_method_type]:
                raise_operation_error(
                    self.request,
                    {"code": [f"Value must be one of {list(CAUSE_DETAILS_MAPPING[procurement_method_type].keys())}."]},
                    status=422,
                    location="body",
                    name="causeDetails",
                )
            if cause_details.get("code") and not cause_details.get("description"):
                raise_operation_error(
                    self.request,
                    {"description": ["This field is required."]},
                    status=422,
                    location="body",
                    name="causeDetails",
                )
            cause_code = cause_details["code"]
            cause_details.update(
                {
                    "scheme": CAUSE_DETAILS_MAPPING[procurement_method_type][cause_code]["scheme"],
                    "title": CAUSE_DETAILS_MAPPING[procurement_method_type][cause_code]["title_uk"],
                    "title_en": CAUSE_DETAILS_MAPPING[procurement_method_type][cause_code]["title_en"],
                }
            )


class ReportingTenderDetailsState(CauseDetailsMixing, TenderDetailsMixing, NegotiationTenderState):
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)
    should_validate_related_lot_in_items = False
    should_validate_required_market_criteria = False

    contract_template_name_patch_statuses = []

    working_days_config = WORKING_DAYS_CONFIG

    def on_post(self, tender):
        self.validate_cause_required(tender)
        self.set_cause_details_data(tender)
        super().on_post(tender)

    def on_patch(self, before, after):
        self.validate_cause_required(after)
        self.set_cause_details_data(after)
        super().on_patch(before, after)


class NegotiationTenderDetailsState(CauseDetailsMixing, TenderDetailsMixing, NegotiationTenderState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)
    should_validate_related_lot_in_items = True
    should_validate_required_market_criteria = False

    contract_template_name_patch_statuses = ("draft", "active")

    working_days_config = WORKING_DAYS_CONFIG

    def on_post(self, tender):
        self.validate_cause_required(tender)
        self.set_cause_details_data(tender)
        super().on_post(tender)

    def on_patch(self, before, after):
        self.validate_cause_required(after)
        self.set_cause_details_data(after)
        if before.get("awards"):
            raise_operation_error(
                get_request(),
                "Can't update tender when there is at least one award.",
            )
        super().on_patch(before, after)

    @staticmethod
    def set_lot_guarantee(tender: dict, data: dict) -> None:
        pass

    @staticmethod
    def set_lot_minimal_step(tender: dict, data: dict) -> None:
        pass


class NegotiationQuickTenderDetailsState(NegotiationTenderDetailsState):
    working_days_config = WORKING_DAYS_CONFIG
