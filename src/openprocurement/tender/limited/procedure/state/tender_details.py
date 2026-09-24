from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.constants import (
    CPV_GROUP_PREFIX_LENGTH,
    PROCUREMENT_METHOD_TYPE_TO_CAUSE_DETAILS_MAPPING,
)
from openprocurement.api.constants_env import (
    CAUSE_DETAILS_REQUIRED_FROM,
    NEGOTIATION_VAT_NOT_INCLUDED_VALIDATION_FROM,
    QUICK_CAUSE_REQUIRED_FROM,
)
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.validation import validate_items_classifications_prefixes
from openprocurement.api.utils import get_tender_category, get_tender_product, raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixin,
)
from openprocurement.tender.core.procedure.utils import (
    reporting_cause_is_required,
    tender_created_after,
    tender_created_before,
)
from openprocurement.tender.limited.constants import WORKING_DAYS_CONFIG
from openprocurement.tender.limited.procedure.models.tender import (
    NegotiationPatchTender,
    NegotiationPostTender,
    NegotiationQuickPatchTender,
    NegotiationQuickPostTender,
    NegotiationQuickTender,
    NegotiationTender,
    ReportingPatchTender,
    ReportingPostTender,
    ReportingTender,
)
from openprocurement.tender.limited.procedure.serializers.cause import (
    enrich_cause_details,
    get_cause_details_reference,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class LimitedCauseDetailsMixin(BaseState):
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

    def set_cause_details_data(self, after, before=None):
        if before and before.get("causeDetails") == after.get("causeDetails"):
            return
        if cause_details := after.get("causeDetails"):
            mapping = PROCUREMENT_METHOD_TYPE_TO_CAUSE_DETAILS_MAPPING
            cause_details_reference = get_cause_details_reference(after, mapping)
            if cause_details.get("code") not in cause_details_reference:
                raise_operation_error(
                    self.request,
                    {"code": [f"Value must be one of {list(cause_details_reference.keys())}."]},
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
            after["causeDetails"] = enrich_cause_details(cause_details, cause_details_reference, force=True)

    def validate_items_related_market_objects(self, after: dict, before: dict) -> None:
        def get_items_market_objects(data: dict) -> dict:
            return {
                item["id"]: {
                    "product": item.get("product"),
                    "category": item.get("category"),
                    "classification": item.get("classification", {}),
                }
                for item in data.get("items", [])
            }

        after_items_rps = get_items_market_objects(after)
        before_items_rps = get_items_market_objects(before)

        for item_id, after_rp in after_items_rps.items():
            before_rp = before_items_rps.get(item_id)

            if before_rp == after_rp:
                continue

            product_id = after_rp["product"]
            category_id = after_rp["category"]

            if product_id and not category_id:
                raise_operation_error(
                    self.request,
                    [{"category": ["This field is required."]}],
                    status=422,
                    name="items",
                )

            if category_id and not product_id:
                raise_operation_error(
                    self.request,
                    [{"product": ["This field is required."]}],
                    status=422,
                    name="items",
                )

            if category_id is None:
                continue

            category = get_tender_category(get_request(), category_id, ("active",))

            get_tender_product(get_request(), product_id, related_category=category_id)

            validate_items_classifications_prefixes(
                [after_rp["classification"]],
                root_classification=category.get("classification", {}),
                root_name="category",
                default_prefix_length=CPV_GROUP_PREFIX_LENGTH,
            )


class ReportingTenderDetailsState(LimitedCauseDetailsMixin, TenderDetailsMixin, NegotiationTenderState):
    post_data_model = ReportingPostTender
    patch_data_model = ReportingPatchTender
    data_model = ReportingTender

    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tender_patch_allowed_statuses = ("draft", "active")
    status_change_with_lot_cancellation_pending_check = False
    items_zero_quantity_check = False
    guarantee_criterion_check = False
    items_related_lot_error = "This option is not available"
    milestones_required = False
    milestones_delivery_financing_required = False
    procuring_entity_required_fields = {}
    related_lot_in_items_check = False
    patch_status_choices = ("draft", "active")
    award_criteria_choices = None
    award_criteria_default = None
    contract_template_name_patch_statuses = []
    working_days_config = WORKING_DAYS_CONFIG
    vat_not_included_check = False
    notice_doc_required_check = False
    items_classification_prefix_change_check = False
    tender_period_start_date_required = False
    # unit price is only meaningful where there is no bidding
    items_unit_value_allowed = True

    def on_post(self, tender):
        self.validate_cause_required(tender)
        self.set_cause_details_data(tender)
        self.validate_items_related_market_objects(tender, {})
        super().on_post(tender)

    def on_patch(self, before, after):
        self.validate_cause_required(after)
        self.set_cause_details_data(after, before)
        self.validate_items_related_market_objects(after, before)
        super().on_patch(before, after)


class NegotiationTenderDetailsState(LimitedCauseDetailsMixin, TenderDetailsMixin, NegotiationTenderState):
    post_data_model = NegotiationPostTender
    patch_data_model = NegotiationPatchTender
    data_model = NegotiationTender

    tender_patch_allowed_statuses = ("draft", "active")
    status_change_with_lot_cancellation_pending_check = False
    items_zero_quantity_check = False
    guarantee_criterion_check = False
    lot_guarantee_currency_from_tender = False
    lot_minimal_step_meta_from_tender = False
    vat_not_included_validation_from = NEGOTIATION_VAT_NOT_INCLUDED_VALIDATION_FROM
    patch_status_choices = ("draft", "active")
    award_criteria_choices = None
    award_criteria_default = None
    contract_template_name_patch_statuses = ("draft", "active")
    working_days_config = WORKING_DAYS_CONFIG
    notice_doc_required_check = False
    items_classification_prefix_change_check = False
    tender_period_start_date_required = False
    # unit price is only meaningful where there is no bidding
    items_unit_value_allowed = True

    def on_post(self, tender):
        self.validate_cause_required(tender)
        self.set_cause_details_data(tender)
        self.validate_items_related_market_objects(tender, {})
        super().on_post(tender)

    def on_patch(self, before, after):
        self.validate_cause_required(after)
        self.set_cause_details_data(after, before)
        if before.get("awards"):
            raise_operation_error(
                get_request(),
                "Can't update tender when there is at least one award.",
            )
        self.validate_items_related_market_objects(after, before)
        super().on_patch(before, after)


class NegotiationQuickTenderDetailsState(NegotiationTenderDetailsState):
    post_data_model = NegotiationQuickPostTender
    patch_data_model = NegotiationQuickPatchTender
    data_model = NegotiationQuickTender
