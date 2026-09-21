from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
from math import ceil, floor

from pyramid.request import Request
from schematics.exceptions import ValidationError

from openprocurement.api.constants import (
    CAUSE_TO_RATIONALE_TYPES_MAPPING,
    CPV_GROUP_PREFIX_LENGTH,
    CPV_PHARM_PREFIX,
    CPV_PREFIX_LENGTH_TO_NAME,
    GUARANTEE_ALLOWED_TENDER_TYPES,
    MINIMAL_STEP_VALIDATION_LOWER_LIMIT,
    MINIMAL_STEP_VALIDATION_PRESCISSION,
    MINIMAL_STEP_VALIDATION_UPPER_LIMIT,
    PROFILE_REQUIRED_MIN_VALUE_AMOUNT,
    TENDER_CO_CONFIG_JSONSCHEMAS,
    TENDER_CONFIG_JSONSCHEMAS,
    TENDER_PERIOD_START_DATE_STALE_MINUTES,
    WORKING_DAYS,
)
from openprocurement.api.constants_env import (
    CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM,
    CRITERIA_CLASSIFICATION_UNIQ_FROM,
    CRITERION_REQUIREMENT_STATUSES_FROM,
    EST_VALUE_VAT_NOT_INCLUDED_VALIDATION_FROM,
    EVALUATION_REPORTS_DOC_REQUIRED_FROM,
    ITEM_QUANTITY_REQUIRED_FROM,
    MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM,
    MINIMAL_STEP_TENDERS_WITH_LOTS_VALIDATION_FROM,
    MINIMAL_STEP_VALIDATION_FROM,
    MPC_REQUIRED_FROM,
    NOTICE_DOC_REQUIRED_FROM,
    RELATED_LOT_REQUIRED_FROM,
    RELEASE_GUARANTEE_CRITERION_FROM,
    TENDER_CONFIG_OPTIONALITY,
    TENDER_ITEMS_DIFFERENT_CPV_FROM,
    UNIFIED_CRITERIA_LOGIC_FROM,
)
from openprocurement.api.constants_utils import parse_date
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_agreement, get_object, get_tender
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.api.procedure.state.base import ConfigMixin
from openprocurement.api.procedure.utils import validate_funders_match_plan_programs
from openprocurement.api.procedure.validation import (
    validate_items_classifications_prefixes,
)
from openprocurement.api.utils import (
    get_first_revision_date,
    get_tender_category,
    get_tender_profile,
    raise_operation_error,
    request_fetch_plans,
    request_fetch_root_tender_for_tender,
)
from openprocurement.contracting.core.procedure.serializers.rationale_types import (
    get_change_rationale_types_reference,
)
from openprocurement.framework.ifi.constants import IFI_TYPE
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.constants import (
    AGREEMENT_CONTRACTS_MESSAGE,
    AGREEMENT_IDENTIFIER_MESSAGE,
    AGREEMENT_NOT_FOUND_MESSAGE,
    AGREEMENT_STATUS_MESSAGE,
    AWARD_CRITERIA_LIFE_CYCLE_COST,
    AWARD_CRITERIA_LOWEST_COST,
    CRITERION_LOCALIZATION,
    CRITERION_TECHNICAL_FEATURES,
    DEFAULT_WORKING_DAYS_CONFIG,
    LIMITED_PROCUREMENT_METHOD_TYPES,
    PROCUREMENT_METHOD_LIMITED,
    PROCUREMENT_METHOD_OPEN,
    PROCUREMENT_METHOD_SELECTIVE,
    SELECTIVE_PROCUREMENT_METHOD_TYPES,
    ReqStatuses,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.tender import PatchTender
from openprocurement.tender.core.procedure.models.tender_base import (
    MAIN_PROCUREMENT_CATEGORY_CHOICES,
    MainProcurementCategory,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    get_contract_template_names_for_classification_ids,
    set_mode_test_titles,
    tender_created_after,
    tender_created_after_2020_rules,
    tender_created_before,
    validate_features_custom_weight,
    validate_field,
)
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_doc_type_required,
    validate_econtract_fields_tender,
    validate_edrpou_confidentiality_doc,
    validate_items_classification_id,
    validate_items_required_fields,
    validate_milestone_duration_days,
    validate_milestone_sums,
    validate_milestones_sequence_number,
    validate_required_nested_fields,
    validate_tender_milestones_required,
    validate_value_vat_disabled,
)
from openprocurement.tender.core.utils import (
    calculate_tender_full_date,
    get_criteria_rules,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


class TenderConfigMixin(ConfigMixin):
    def get_config_schema(self, data):
        procurement_method_type = data.get("procurementMethodType")
        config_schema = TENDER_CONFIG_JSONSCHEMAS.get(procurement_method_type)

        if not config_schema:
            # procurementMethodType not found in TENDER_CONFIG_JSONSCHEMAS
            raise NotImplementedError

        config_schema = deepcopy(config_schema)

        return config_schema

    # competitiveOrdering: an additional config schema (short/long) is validated on top of the procedure schema
    extra_config_schema_name: str | None = None

    def validate_extra_config(self, data):
        config_schema = TENDER_CO_CONFIG_JSONSCHEMAS.get(self.extra_config_schema_name)
        config_schema = deepcopy(config_schema)
        config_schema.pop("required", None)
        self.validate_config_schema(data, config_schema)

    def validate_config(self, data):
        # load schema from standards
        config_schema = self.get_config_schema(data)

        # we will validate required fields manually
        config_schema.pop("required", None)

        # validate required fields
        properties = config_schema.get("properties", {})
        for config_name in properties.keys():
            value = data["config"].get(config_name)
            if value is None and TENDER_CONFIG_OPTIONALITY.get(config_name, True) is False:
                raise_operation_error(
                    self.request,
                    "This field is required.",
                    status=422,
                    location="body",
                    name=f"config.{config_name}",
                )

        # validate config with schema
        super().validate_config(data)
        if self.extra_config_schema_name:
            self.validate_extra_config(data)

    def on_post(self, data):
        self.validate_config(data)
        self.validate_restricted_config(data)
        self.validate_estimated_value_config(data)
        self.validate_value_currency_equality(data)
        super().on_post(data)

    def validate_value_currency_equality(self, data):
        """Validate valueCurrencyEquality config option"""
        config = data["config"]
        value = config.get("valueCurrencyEquality")

        if value is False and any(
            [
                config.get("hasAuction"),
                config.get("hasAwardingOrder"),
                config.get("hasValueRestriction"),
            ]
        ):
            raise_operation_error(
                self.request,
                [
                    "valueCurrencyEquality can be False only if "
                    "hasAuction=False and "
                    "hasAwardingOrder=False and "
                    "hasValueRestriction=False"
                ],
                status=422,
                location="body",
                name="config.valueCurrencyEquality",
            )

    def validate_estimated_value_config(self, data):
        if (
            data["procurementMethodType"] != "esco"
            and data["config"]["hasValueEstimation"] is False
            and data["config"]["hasValueRestriction"] is True
        ):
            raise_operation_error(
                self.request,
                "hasValueRestriction should be False",
                status=422,
                location="body",
                name="config.hasValueRestriction",
            )

    def validate_restricted_config(self, data):
        has_restricted_preselection_agreement = False
        agreement = get_agreement()
        if agreement:
            has_restricted_preselection_agreement = agreement["config"].get("restricted") is True
        if has_restricted_preselection_agreement is True and data["config"]["restricted"] is False:
            raise_operation_error(
                self.request,
                "Value must be True.",
                status=422,
                location="body",
                name="config.restricted",
            )
        elif has_restricted_preselection_agreement is False and data["config"]["restricted"] is True:
            raise_operation_error(
                self.request,
                "Value must be False.",
                status=422,
                location="body",
                name="config.restricted",
            )


class BaseTenderDetailsMixing:
    """
    describes business logic rules for tender owners
    when they prepare tender for tendering stage
    """

    request: Request

    tender_create_accreditations = None
    tender_central_accreditations = None
    tender_edit_accreditations = None
    agreement_min_active_contracts = 3
    should_validate_cpv_prefix = True
    should_validate_pre_selection_agreement = True
    should_validate_profiles_agreement_id = False
    should_match_agreement_procuring_entity = True
    should_validate_notice_doc_required = False
    should_validate_evaluation_reports_doc_required = True
    procurement_kinds_not_required_sign = ()
    agreement_field = "agreements"
    should_validate_lot_minimal_step = True
    should_validate_related_lot_in_items = True
    agreement_allowed_types = [IFI_TYPE]
    agreement_with_items_forbidden = False
    agreement_without_items_forbidden = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    items_profile_required = False
    should_validate_items_classifications_prefix = True
    tender_period_extra_working_days = False
    working_days_config = DEFAULT_WORKING_DAYS_CONFIG
    should_validate_required_market_criteria = True
    should_validate_status_change_with_lot_cancellation_pending = True
    should_validate_items_zero_quantity = True
    should_validate_guarantee_criterion = True
    guarantee_criterion_check_skipped_for_administrator = False  # CD stage2
    should_validate_vat_not_included = False
    vat_not_included_validation_from = EST_VALUE_VAT_NOT_INCLUDED_VALIDATION_FROM
    # complexAsset.arma has no contractTemplateName (the field used to be removed from its models)
    contract_template_name_allowed = True
    items_delivery_required = False
    # items classification / INN rule (former validate_classification_id)
    items_classification_id_check = True
    items_classification_id_check_on_post = True  # esco used to check it on the full model only
    # milestones requirements (former TenderMilestoneMixin.validate_milestones)
    milestones_required = True
    milestones_delivery_financing_required = True
    milestones_delivery_financing_required_on_post = True  # CD stage2 checks it on the full model only
    # mainProcurementCategory required since MPC_REQUIRED_FROM (former model validator)
    main_procurement_category_required = True
    # lifeCycleCost is not allowed together with features (former model validator)
    award_criteria_lcc_features_check = True
    # fields of procuringEntity that must be present (reporting allows a procuring entity without contactPoint)
    procuring_entity_required_fields: dict = {"contactPoint": True}
    # error for items with relatedLot in procedures without lots (None = relatedLot is allowed)
    items_related_lot_error: str | None = None
    items_unit_required = True
    items_quantity_required = True  # since UNIT_PRICE_REQUIRED_FROM
    features_max_weight = 0.3  # max value of a single feature and of the sum per lot/tender
    # open family: tenderPeriod.startDate defaults to now on create and is required afterwards
    tender_period_start_date_required = False
    # belowThreshold / requestForProposal: enquiryPeriod (with endDate) is set by the user and required
    enquiry_period_required = False
    # statuses a tender owner may set with PATCH (former PatchTender.status choices); None = not validated here
    patch_status_choices: tuple | None = None
    # allowed mainProcurementCategory values (former per-procedure model choices)
    main_procurement_category_choices: tuple = tuple(MAIN_PROCUREMENT_CATEGORY_CHOICES)
    # allowed / default awardCriteria (None = the tender has no awardCriteria)
    award_criteria_choices: tuple | None = (AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST)
    award_criteria_default: str | None = AWARD_CRITERIA_LOWEST_COST
    # {field: True | nested dict}, see validate_required_nested_fields
    required_multilingual_fields: dict = {}
    # procuringEntity.contactPoint.availableLanguage default (None = field is optional, no default)
    procuring_entity_available_language_default: str | None = None

    calendar = WORKING_DAYS

    # --- mainstream procedure differences (former method overrides) ---
    # bt/rfp: the patch model depends on the tender status
    tender_patch_models_by_status: dict | None = None
    # open family/CO: the CPV group of the items can't change on patch
    items_classification_prefix_change_check = False
    # rfp: noticePublicationDate is set on activation even without a notice document
    notice_publication_date_on_activation = False
    # pq: tenderPeriod.startDate is set on activation, no tenderPeriod extension
    tender_period_start_on_activation = False
    tender_period_extension_check = True
    # CO: a defense procuring entity may use an agreement of another defense procuring entity
    agreement_procuring_entity_match_except_defense = False
    # arma: no tender.value / tender.minimalStep (value, minimal step and their limits are not validated)
    tender_has_value = True
    # lots inherit currency/VAT of the tender value (arma/cfaselectionua: no), minimal step meta (+ negotiation: no),
    # guarantee currency (negotiation: no)
    lot_value_meta_from_tender = True
    lot_minimal_step_meta_from_tender = True
    lot_guarantee_currency_from_tender = True
    # esco/cfaua/cfaselectionua/CD stage2/arma: currency/VAT of the tender value are not propagated to items/lots
    watch_value_meta_changes_enabled = True
    # esco: minimalStepPercentage/yearlyPaymentsPercentageRange instead of minimalStep
    minimal_step_fields = ("minimalStep",)
    minimal_step_required = True  # cfaselectionua: calculated on activation
    minimal_step_regardless_of_auction = False  # competitiveDialogue: required although stage 1 has no auction
    lot_minimal_step_check_before = True  # competitiveDialogue stage 1: the lot minimal step is always checked
    submission_method_required = True  # competitiveDialogue stage 1: optional, no auction dependency
    all_documents_should_be_public = False  # cfaua/cfaselectionua
    # cfaua: the allowed tender status transitions (None = the generic rules only)
    status_up_allowed_transitions: tuple | None = None
    # competitiveDialogue stage 2: item profile/category are not checked on post
    item_profile_category_check_on_post = True

    def get_patch_data_model(self):
        models = self.tender_patch_models_by_status or {}
        return models.get(self.request.validated["tender"].get("status", ""), PatchTender)

    def validate_tender_patch(self, before, after):
        self.validate_status_change_with_lot_cancellation_pending(before, after)
        self.validate_items_zero_quantity(before, after)
        self.validate_guarantee_criterion(before, after)
        self.validate_patch_status_choice(before, after)
        request = get_request()
        if before["status"] != after["status"]:
            self.validate_cancellation_blocks(request, before)
        if before.get("funders") != after.get("funders"):
            self.validate_funders_match_plan_program(request, after)

    def validate_funders_match_plan_program(self, request, tender):
        plan_ids = [plan["id"] for plan in tender.get("plans") or []]
        plans = request_fetch_plans(request, plan_ids, raise_error=False)
        validate_funders_match_plan_programs(request, tender, plans)

    def validate_status_change_with_lot_cancellation_pending(self, before, after):
        if not self.should_validate_status_change_with_lot_cancellation_pending:
            return
        request = get_request()
        if request.authenticated_role == "Administrator":
            return
        if not tender_created_after_2020_rules():
            return
        if not before.get("lots") or before["status"] == after.get("status", before["status"]):
            return
        lot_cancellations = [c for c in before.get("cancellations", "") if c.get("relatedLot")]
        accept_lot = all(
            any(complaint.get("status") == "resolved" for complaint in c.get("complaints", ""))
            for c in lot_cancellations
            if c.get("status") == "unsuccessful" and c.get("complaints")
        )
        if any(c.get("status") == "pending" for c in lot_cancellations) or not accept_lot:
            raise_operation_error(request, "Can't update tender with pending cancellation in one of exists lot")

    def validate_items_zero_quantity(self, before, after):
        if not self.should_validate_items_zero_quantity:
            return
        if not tender_created_after(CRITERION_REQUIREMENT_STATUSES_FROM):
            return
        for item in after.get("items", ""):
            if item.get("quantity") is not None and not item["quantity"]:
                related_criteria = any(
                    criterion.get("relatedItem") == item["id"] and requirement.get("status") == "active"
                    for criterion in before.get("criteria", "")
                    for rg in criterion.get("requirementGroups", "")
                    for requirement in rg.get("requirements", "")
                )
                if related_criteria:
                    raise_operation_error(
                        get_request(),
                        f"Can't set to 0 quantity of {item['id']} item while related criterion has active requirements",
                    )

    def validate_guarantee_criterion(self, before, after):
        if not self.should_validate_guarantee_criterion:
            return
        request = get_request()
        if self.guarantee_criterion_check_skipped_for_administrator and request.authenticated_role == "Administrator":
            return
        if tender_created_before(RELEASE_GUARANTEE_CRITERION_FROM):
            return

        new_status = after.get("status")
        if before["status"] == new_status:
            return

        if new_status not in ("active", "active.enquiries", "active.tendering"):
            return

        tender_type = before["procurementMethodType"]
        if tender_created_before(UNIFIED_CRITERIA_LOGIC_FROM) and tender_type not in GUARANTEE_ALLOWED_TENDER_TYPES:
            return

        bid_guarantee_criterion = "CRITERION.OTHER.BID.GUARANTEE"

        if before.get("lots"):
            related_guarantee_lots = [
                criterion.get("relatedItem")
                for criterion in before.get("criteria", "")
                if criterion.get("relatesTo") == "lot"
                and criterion.get("classification")
                and criterion["classification"]["id"] == bid_guarantee_criterion
            ]
            for lot in before["lots"]:
                if lot["id"] in related_guarantee_lots:
                    if not lot.get("guarantee") or lot["guarantee"]["amount"] <= 0:
                        raise_operation_error(
                            request,
                            f"Should be specified 'guarantee.amount' more than 0 to lot for {bid_guarantee_criterion}",
                        )
                elif (
                    tender_created_after(UNIFIED_CRITERIA_LOGIC_FROM) and lot.get("guarantee", {}).get("amount", 0) > 0
                ):
                    raise_operation_error(
                        request,
                        f"Should be specified {bid_guarantee_criterion} for 'guarantee.amount' more than 0 to lot",
                    )

        else:
            amount = after["guarantee"]["amount"] if after.get("guarantee") else 0
            tender_criteria = [
                criterion["classification"]["id"]
                for criterion in before.get("criteria", "")
                if criterion.get("classification")
            ]
            if (amount <= 0 and bid_guarantee_criterion in tender_criteria) or (
                amount > 0 and bid_guarantee_criterion not in tender_criteria
            ):
                raise_operation_error(
                    request,
                    f"Should be specified {bid_guarantee_criterion} and 'guarantee.amount' more than 0",
                )

    def on_post(self, tender):
        self.validate_contract_template_name_allowed(tender)
        self.validate_main_procurement_category(tender)
        self.validate_award_criteria(tender, on_post=True)
        self.validate_items_related_lot_allowed(tender)
        self.validate_items_required_fields(tender)
        self.validate_items_classification_id(tender, on_post=True)
        self.validate_tender_milestones_required(tender, on_post=True)
        self.validate_procuring_entity_required_fields(tender)
        self.set_procuring_entity_available_language(tender)
        self.validate_multilingual_fields(tender)
        self.validate_features(tender)
        self.validate_enquiry_period_required(tender, on_post=True)
        self.validate_tender_period_start_date_required(tender, on_post=True)
        self.validate_enquiry_period(tender)
        self.update_tender_period(tender)
        self.validate_procurement_method(tender)

        # tenders created via POST /plans/{id}/tenders get "plans" set after this runs
        # and are validated by PlanState; this covers direct POST /tenders with "plans"
        if tender.get("plans"):
            self.validate_funders_match_plan_program(get_request(), tender)

        self.validate_tender_value(tender)
        self.validate_tender_lots(tender)
        self.validate_milestones(tender)
        self.validate_submission_method(tender)
        self.validate_items_classification_prefix(tender)
        self.validate_pre_selection_agreement(tender)
        self.validate_items_with_agreement(tender)
        self.validate_docs(tender)
        self.watch_value_meta_changes(tender)
        self.initialize_enquiry_period(tender)
        self.update_complaint_period(tender)
        self.update_date(tender)
        self.validate_tender_period_after_enquiry_period(tender)
        self.validate_tender_period_start_date(tender)
        self.validate_tender_period_duration(tender)
        self.validate_change_item_profile_or_category(tender, {})
        self.validate_contract_template_name(tender, {})
        self.validate_criteria_classification(tender.get("criteria", []))
        self.validate_criteria_requirements_rules(tender.get("criteria", []))
        if tender_period_end_date := tender.get("tenderPeriod", {}).get("endDate"):
            self.calc_qualification_period(tender, dt_from_iso(tender_period_end_date))
        self.set_contract_change_rationale_types(tender)
        super().on_post(tender)

        # set author for documents passed with tender data
        for doc in tender.get("documents", ""):
            doc["author"] = "tender_owner"

    def on_patch(self, before, after):
        if self.items_classification_prefix_change_check:
            self.validate_items_classification_prefix_unchanged(before, after)
        self.validate_contract_template_name_allowed(after)
        self.validate_main_procurement_category(after)
        self.validate_award_criteria(after)
        self.validate_items_related_lot_allowed(after)
        self.validate_items_required_fields(after)
        self.validate_items_classification_id(after)
        self.validate_tender_milestones_required(after)
        self.validate_procuring_entity_required_fields(after)
        self.set_procuring_entity_available_language(after)
        self.validate_multilingual_fields(after)
        self.validate_features(after)
        self.validate_enquiry_period_required(after)
        self.validate_tender_period_start_date_required(after)
        self.validate_enquiry_period(after)
        self.validate_enquiry_period_delete(before, after)
        self.update_tender_period(after)
        self.validate_tender_period_delete(before, after)

        # bid invalidation rules
        if before["status"] == "active.tendering":
            self.validate_tender_period_extension(after)
            self.invalidate_bids_data(after)
        elif after["status"] == "active.tendering":
            self.set_bids_invalidation_date(after)

        self.validate_contract_template_name(after, before=before)
        self.validate_procurement_method(after, before=before)
        self.validate_milestones(after, before=before)
        self.validate_pre_qualification_status_change(before, after)
        self.validate_tender_period_duration(after)
        self.validate_tender_period_after_enquiry_period(after)
        self.validate_tender_period_start_date_change(before, after)
        self.validate_tender_value(after)
        self.validate_tender_lots(after, before=before)
        self.validate_submission_method(after, before=before)
        self.validate_kind_change(after, before)
        self.validate_award_criteria_change(after, before)
        self.validate_items_classification_prefix(after)
        self.validate_pre_selection_agreement(after)
        self.validate_items_with_agreement(after)
        self.validate_action_with_exist_inspector_review_request(("tenderPeriod",))
        self.validate_docs(after, before)
        self.update_complaint_period(after)
        self.watch_value_meta_changes(after)
        if tender_created_after(CRITERIA_CLASSIFICATION_UNIQ_FROM):
            self._validate_criterion_uniq(after.get("criteria", []))
        if before.get("criteria") != after.get("criteria"):
            self.validate_criteria_classification(after.get("criteria", []))
            self.validate_criteria_requirements_rules(after.get("criteria", []))
        self.invalidate_review_requests()
        self.validate_remove_inspector(before, after)
        if after["status"] in ("draft", "draft.stage2", "active.enquiries", "active.tendering"):
            self.initialize_enquiry_period(after)

        if self.should_validate_related_lot_in_items:
            self.validate_related_lot_in_items(after)

        if after["status"] not in ("draft", "draft.stage2"):
            if before["status"] in ("draft", "draft.stage2"):  # validations on activation
                if tender_created_after(MINIMAL_STEP_TENDERS_WITH_LOTS_VALIDATION_FROM):
                    self.validate_minimal_step(after, before=before)
                self.validate_pre_selection_agreement_on_activation(after)
                self.validate_profiles_agreement_id(after)
                self.validate_change_item_profile_or_category(after, before, force_validate=True)
                self.validate_notice_doc_required(after)
                self.validate_required_criteria(before, after)
                self.validate_criteria_requirement_from_market(after.get("criteria", []))
            else:
                for field in ("minimalStep", "minimalStepPercentage", "yearlyPaymentsPercentageRange"):
                    if after.get(field) != before.get(field):
                        self.validate_minimal_step(after, before=before)
        else:
            self.validate_change_item_profile_or_category(after, before)

        # update qualification period if required
        tender_period_end_date_after = after.get("tenderPeriod", {}).get("endDate")
        tender_period_end_date_before = before.get("tenderPeriod", {}).get("endDate")
        if tender_period_end_date_after and tender_period_end_date_after != tender_period_end_date_before:
            self.calc_qualification_period(after, dt_from_iso(tender_period_end_date_after))

        # update contract change rationale types if required
        cause_details_after = after.get("causeDetails")
        cause_details_before = before.get("causeDetails")
        if cause_details_after != cause_details_before:
            self.set_contract_change_rationale_types(after)

        super().on_patch(before, after)

        if self.notice_publication_date_on_activation and after["status"] != "draft" and before["status"] == "draft":
            # even without document `notice` it is required to set `noticePublicationDate` for RFP (CS-19667)
            after["noticePublicationDate"] = get_request_now().isoformat()

    def always(self, data):
        self.validate_econtract_fields(data)
        self.validate_items_quantity(data)
        self.validate_items_profile(data)
        self.set_mode_test(data)
        super().always(data)

    def update_tender_period(self, tender):
        tender_period = tender.get("tenderPeriod", {})
        enquiry_period = tender.get("enquiryPeriod", {})
        if tender["config"]["hasEnquiries"]:
            if enquiry_period.get("endDate") and not tender_period.get("startDate"):
                tender["tenderPeriod"] = {
                    "startDate": enquiry_period.get("endDate"),
                    "endDate": tender_period.get("endDate"),
                }

    def validate_enquiry_period_delete(self, before, after):
        enquiry_period_before = before.get("enquiryPeriod", {})
        enquiry_period_after = after.get("enquiryPeriod", {})
        if enquiry_period_before.get("startDate") and not enquiry_period_after.get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="enquiryPeriod",
            )

    def validate_tender_period_delete(self, before, after):
        tender_period_before = before.get("tenderPeriod", {})
        tender_period_after = after.get("tenderPeriod", {})
        if tender_period_before.get("startDate") and not tender_period_after.get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="tenderPeriod",
            )

    def validate_econtract_fields(self, after):
        validate_econtract_fields_tender(self.request, after)

    def status_up(self, before, after, data):
        if self.status_up_allowed_transitions is not None and (before, after) not in self.status_up_allowed_transitions:
            raise_operation_error(
                get_request(),
                f"Can't update tender to {after} status",
                status=403,
                location="body",
                name="status",
            )
        if after == "draft" and before != "draft":
            raise_operation_error(
                get_request(),
                "Can't change status to draft",
                status=422,
                location="body",
                name="status",
            )
        if after == "active.tendering" and before != "active.tendering":
            self.validate_tender_period_start_date(data)
        super().status_up(before, after, data)
        if self.tender_period_start_on_activation and before == "draft" and after == "active.tendering":
            data["tenderPeriod"]["startDate"] = get_request_now().isoformat()

    def validate_notice_doc_required(self, tender):
        if (
            self.should_validate_notice_doc_required is False
            or not tender_created_after(NOTICE_DOC_REQUIRED_FROM)
            or tender.get("procuringEntity", {}).get("kind") in self.procurement_kinds_not_required_sign
        ):
            return
        validate_doc_type_required(tender.get("documents", []), document_of="tender")
        tender["noticePublicationDate"] = get_request_now().isoformat()

    def get_tender_agreements(self, tender):
        tender_agreements = tender.get(self.agreement_field)
        if not tender_agreements:
            return []

        if not isinstance(tender_agreements, list):
            # PQ has field "agreement" with single object instead of "agreements" with list of objects
            tender_agreements = [tender_agreements]

        return tender_agreements

    def validate_pre_selection_agreement(self, tender):
        if self.should_validate_pre_selection_agreement is False:
            return

        tender_agreements = self.get_tender_agreements(tender)

        if tender["config"]["hasPreSelectionAgreement"] is False:
            if tender_agreements:
                message = "Agreements cannot be specified when 'hasPreSelectionAgreement' is False."
                raise_operation_error(self.request, message, status=422, name=self.agreement_field)
            return

        if not tender_agreements:
            message = "This field is required."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if len(tender_agreements) != 1:
            message = "Exactly one agreement is expected."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        agreement = get_object("agreement")

        if not agreement:
            message = AGREEMENT_NOT_FOUND_MESSAGE
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if agreement["agreementType"] not in self.agreement_allowed_types:
            message = "Agreement type mismatch."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.agreement_with_items_forbidden and agreement.get("items"):
            message = "Agreement with items is not allowed."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.agreement_without_items_forbidden and not agreement.get("items"):
            message = "Agreement without items is not allowed."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.has_mismatched_procuring_entities(tender, agreement):
            message = AGREEMENT_IDENTIFIER_MESSAGE
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

    def validate_pre_selection_agreement_on_activation(self, tender):
        """
        Validations of agreement on activation
        We dont care if agreement was changed after tender was activated
        and those valdations no longer pass
        """
        if self.should_validate_pre_selection_agreement is False:
            return

        if tender["config"]["hasPreSelectionAgreement"] is False:
            return

        agreement = get_object("agreement")

        if self.is_agreement_not_active(agreement):
            message = AGREEMENT_STATUS_MESSAGE
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.has_insufficient_active_contracts(agreement):
            message = AGREEMENT_CONTRACTS_MESSAGE.format(self.agreement_min_active_contracts)
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

    def validate_profiles_agreement_id(self, tender):
        if self.should_validate_profiles_agreement_id is False:
            return

        profile_ids = []

        tender_agreements = self.get_tender_agreements(tender)

        if not tender_agreements:
            return

        for items in tender.get("items", []):
            profile_id = items.get("profile")
            if profile_id:
                profile_ids.append(profile_id)

        for profile_id in profile_ids:
            profile = get_tender_profile(self.request, profile_id, validate_status=("active",))

            profile_agreement_id = profile.get("agreementID")
            tender_agreement_id = tender_agreements[0].get("id")
            if profile_agreement_id != tender_agreement_id:
                raise_operation_error(
                    self.request,
                    "Tender agreement doesn't match profile agreement",
                    status=422,
                )

    def set_mode_test(self, tender):
        if tender.get("mode") == "test":
            set_mode_test_titles(tender)

    def validate_milestones(self, tender, before=None):
        grouped_data = defaultdict(list)
        related_lot_exists = False

        milestones_before = before.get("milestones", []) if before else []
        milestones_after = tender.get("milestones", [])

        if milestones_before == milestones_after:
            return

        request_fetch_root_tender_for_tender(self.request, tender["_id"], raise_error=False)
        root_tender = self.request.validated.get("root_tender") or self.request.validated["tender"]

        for milestone in tender.get("milestones", []):
            validate_milestone_duration_days(tender, milestone)

            related_lot = milestone.get("relatedLot")
            grouped_data[related_lot].append(milestone)

            if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM, root_tender) and related_lot:
                related_lot_exists = True

        if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM, root_tender):
            for lot, milestones in grouped_data.items():
                for milestone in milestones:
                    if related_lot_exists and not milestone.get("relatedLot"):
                        raise_operation_error(
                            get_request(),
                            [
                                {
                                    "relatedLot": "Related lot must be set in all milestones or all milestones should be related to tender"
                                }
                            ],
                            status=422,
                            name="milestones",
                        )
                validate_milestones_sequence_number(
                    milestones,
                    "Field should contain incrementing sequence numbers starting from 1 for tender/lot separately",
                )

        validate_milestone_sums(milestones_after)

    def validate_tender_lots(self, tender: dict, before=None) -> None:
        """Validate tender lots

        Validation includes lot value and lot minimal step, if required.

        :param tender: Tender dictionary.
        :param before: Tender dictionary before patch, optional
        :return: None
        """
        lots = tender.get("lots")

        if lots:
            lots_amounts = [lot.get("value").get("amount") for lot in lots if lot.get("value")]
            if tender["config"]["hasValueEstimation"] is False and any(lots_amounts):
                raise_operation_error(
                    self.request,
                    "Value amount should not be passed if tender does not have estimated value",
                    status=422,
                    location="body",
                    name="lots.value.amount",
                )

            for lot in lots:
                self.set_lot_guarantee(tender, lot)
                self.set_lot_value(tender, lot)
                self.set_lot_minimal_step(tender, lot)
                self.validate_lot_minimal_step(lot, before)
                self.validate_lot_value(tender, lot)

    def set_lot_guarantee(self, tender: dict, lot: dict) -> None:
        if not self.lot_guarantee_currency_from_tender:
            return
        if guarantee := lot.get("guarantee"):
            currency = tender["guarantee"]["currency"] if tender.get("guarantee") else guarantee.get("currency")
            lot["guarantee"]["currency"] = currency

    def set_lot_value(self, tender: dict, lot: dict) -> None:
        if not self.lot_value_meta_from_tender:
            return
        if tender_value := tender.get("value"):
            lot["value"].update(
                {
                    "currency": tender_value["currency"],
                    "valueAddedTaxIncluded": tender_value["valueAddedTaxIncluded"],
                }
            )

    def set_lot_minimal_step(self, tender: dict, lot: dict) -> None:
        if not self.lot_minimal_step_meta_from_tender:
            return
        if lot.get("minimalStep") and (tender_value := tender.get("value")):
            lot["minimalStep"].update(
                {
                    "currency": tender_value.get("currency"),
                    "valueAddedTaxIncluded": tender_value.get("valueAddedTaxIncluded"),
                }
            )

    def validate_lot_value(self, tender: dict, lot: dict) -> None:
        """Validate lot value.

        Validation includes lot value and lot minimal step, if required.

        :param tender: Tender dictionary
        :param lot: Lot dictionary
        :return: None
        """
        has_value_estimation = tender["config"]["hasValueEstimation"]
        lot_value = lot.get("value", {})

        if not lot_value:
            return

        lot_min_step = lot.get("minimalStep", {})
        lot_value_amount = lot_value.get("amount")
        if has_value_estimation is True and lot_value_amount is None:
            raise_operation_error(
                self.request,
                "This field is required",
                status=422,
                name="lots.value.amount",
            )

        if has_value_estimation is False and lot_value_amount:
            raise_operation_error(
                self.request,
                "Rogue field",
                status=422,
                name="lots.value.amount",
            )

        if lot_min_step and lot_value["currency"] != lot_min_step["currency"]:
            raise_operation_error(
                get_request(),
                "Lot minimal step currency should be identical to tender currency",
                status=422,
                location="body",
                name="lots.minimalStep.currency",
            )

        if lot_min_step and lot_value["valueAddedTaxIncluded"] != lot_min_step["valueAddedTaxIncluded"]:
            raise_operation_error(
                get_request(),
                "Lot minimal step valueAddedTaxIncluded should be identical to tender valueAddedTaxIncluded",
                status=422,
                location="body",
                name="lots.minimalStep.valueAddedTaxIncluded",
            )

        # CS-21518 - for some tenders we need to validate that lot has valueAddedTaxIncluded False
        if self.should_validate_vat_not_included:
            validate_value_vat_disabled(self.request, lot_value, "lots.value", self.vat_not_included_validation_from)

        lot_min_step_amount = lot_min_step.get("amount")

        if lot_min_step_amount is None:
            return

        if has_value_estimation and lot_value_amount is not None and lot_value_amount < lot_min_step_amount:
            raise_operation_error(
                self.request,
                "Minimal step value should be less than lot value",
                status=422,
                name="lots",
            )
        if self.should_validate_lot_minimal_step and has_value_estimation and lot_value_amount is not None:
            self.validate_minimal_step_limits(tender, lot_value_amount, lot_min_step_amount)

    def validate_minimal_step_limits(self, tender: dict, value_amount: float, minimal_step_amount: float) -> None:
        """Validate minimal step lower and upper limits.

        :param request: Request instance
        :param tender: Tender dictionary
        :param value_amount: Value amount
        :param minimal_step_amount: Minimal step amount
        :return: None
        """
        if not self.tender_has_value:  # arma: no minimal step limits
            return
        tender_created = get_first_revision_date(tender, default=get_request_now())
        if tender_created > MINIMAL_STEP_VALIDATION_FROM:
            precision_multiplier = 10**MINIMAL_STEP_VALIDATION_PRESCISSION

            lower_step = (
                floor(float(value_amount) * MINIMAL_STEP_VALIDATION_LOWER_LIMIT * precision_multiplier)
                / precision_multiplier
            )

            higher_step = (
                ceil(float(value_amount) * MINIMAL_STEP_VALIDATION_UPPER_LIMIT * precision_multiplier)
                / precision_multiplier
            )

            if higher_step < minimal_step_amount or minimal_step_amount < lower_step:
                raise_operation_error(
                    self.request,
                    "Minimal step value must be between 0.5% and 3% of value (with 2 digits precision).",
                    status=422,
                )

    def validate_pre_qualification_status_change(self, before, after):
        tender = get_tender()
        qualif_complain_duration = tender["config"]["qualificationComplainDuration"]

        # TODO: find a better place for this check, may be a distinct endpoint: PUT /tender/uid/status
        if before["status"] == "active.pre-qualification":
            passed_data = get_request().validated["json_data"]
            if passed_data != {"status": "active.pre-qualification.stand-still"}:
                raise_operation_error(
                    get_request(),
                    "Can't update tender at 'active.pre-qualification' status",
                )
            else:  # switching to active.pre-qualification.stand-still
                lots = after.get("lots")
                if lots:
                    active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
                else:
                    active_lots = {None}

                if any(
                    self.is_blocking_complaint(i)
                    for q in after["qualifications"]
                    for i in q.get("complaints", "")
                    if q.get("lotID") in active_lots
                ):
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.pre-qualification.stand-still' before resolve all complaints",
                    )

                if self.should_validate_evaluation_reports_doc_required and tender_created_after(
                    EVALUATION_REPORTS_DOC_REQUIRED_FROM
                ):
                    validate_doc_type_required(
                        get_tender().get("documents", []),
                        document_type="evaluationReports",
                        document_of="tender",
                        after_date=get_tender()["qualificationPeriod"].get("reportingDatePublication"),
                    )
                if self.all_bids_are_reviewed(after):
                    end_date = calculate_tender_full_date(
                        get_request_now(),
                        timedelta(days=qualif_complain_duration),
                        working_days=self.working_days_config["qualificationComplainDuration"],
                        tender=after,
                        # if qualif_complain_duration is 0 - force ceil,
                        # otherwise let the ceil flag to be defined inside the calculate_tender_full_date function
                        ceil=None if qualif_complain_duration else True,
                    ).isoformat()

                    if qualif_complain_duration > 0:
                        for qualification in after["qualifications"]:
                            if qualification.get("status") in [
                                "unsuccessful",
                                "active",
                            ]:
                                qualification["complaintPeriod"] = {
                                    "startDate": get_request_now().isoformat(),
                                    "endDate": end_date,
                                }

                    after["qualificationPeriod"]["endDate"] = end_date
                    after["qualificationPeriod"]["reportingDatePublication"] = get_request_now().isoformat()
                else:
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.pre-qualification.stand-still' while not all bids are qualified",
                    )

        # before status != active.pre-qualification
        elif after["status"] == "active.pre-qualification.stand-still":
            raise_operation_error(
                get_request(),
                f"Can't switch to 'active.pre-qualification.stand-still' from {before['status']}",
            )
        elif before["status"] == "active.pre-qualification.stand-still":
            passed_data = get_request().validated["json_data"]
            if passed_data != {"status": "active.pre-qualification"}:
                raise_operation_error(
                    get_request(),
                    "Can't update tender at 'active.pre-qualification.stand-still' status",
                )

            lots = after.get("lots")
            if lots:
                active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
            else:
                active_lots = {None}

            if any(
                i.get("type", "complaint") == "complaint" and i.get("status") in ("draft", "pending", "accepted")
                for q in after["qualifications"]
                for i in q.get("complaints", "")
                if q.get("lotID") in active_lots
            ):
                raise_operation_error(
                    get_request(),
                    "Can't switch to 'active.pre-qualification' before resolve all complaints",
                )
        elif after["status"] == "active.pre-qualification":
            # tendering is ended by the chronograph (see tendering_end_handler), which gates on
            # hasPrequalification/tenderPeriod.endDate and creates qualifications along the way,
            # so the only manual switch to this status is the one from stand-still handled above
            raise_operation_error(
                get_request(),
                f"Can't switch to 'active.pre-qualification' from {before['status']}",
            )

    @staticmethod
    def all_bids_are_reviewed(tender):
        bids = tender.get("bids", "")
        lots = tender.get("lots")
        if lots:
            active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
            return all(
                lotValue.get("status") != "pending"
                for bid in bids
                if bid.get("status") not in ("invalid", "deleted")
                for lotValue in bid.get("lotValues", "")
                if lotValue["relatedLot"] in active_lots
            )
        else:
            return all(bid.get("status") != "pending" for bid in bids)

    @staticmethod
    def all_awards_are_reviewed(tender):
        """
        checks if all tender awards are reviewed
        """
        return all(award["status"] != "pending" for award in tender["awards"])

    @staticmethod
    def update_date(tender):
        now = get_request_now().isoformat()
        tender["date"] = now

        for lot in tender.get("lots", ""):
            lot["date"] = now

    def watch_value_meta_changes(self, tender):
        # tender currency and valueAddedTaxIncluded must be specified only ONCE
        # instead it's specified in many places but we need keep them the same
        if not self.watch_value_meta_changes_enabled:
            return
        value = tender.get("value")
        if not value:
            return
        currency = value.get("currency")
        tax_inc = value.get("valueAddedTaxIncluded")

        # items
        for item in tender["items"]:
            if "unit" in item and "value" in item["unit"]:
                item["unit"]["value"]["currency"] = currency
                item["unit"]["value"]["valueAddedTaxIncluded"] = tax_inc

        # lots
        for lot in tender.get("lots", ""):
            value = lot.get("value")
            if value:
                value["currency"] = currency
                value["valueAddedTaxIncluded"] = tax_inc

            minimal_step = lot.get("minimalStep")
            if minimal_step:
                minimal_step["currency"] = currency
                minimal_step["valueAddedTaxIncluded"] = tax_inc

    def initialize_enquiry_period(self, tender):
        if tender["config"]["hasEnquiries"] is False and tender["config"]["enquiryPeriodRegulation"] > 0:
            tender["enquiryPeriod"] = tender.get("enquiryPeriod") or {}
            tender["enquiryPeriod"]["startDate"] = tender["tenderPeriod"]["startDate"]
            tender["enquiryPeriod"]["endDate"] = calculate_tender_full_date(
                dt_from_iso(tender["tenderPeriod"]["endDate"]),
                -timedelta(days=tender["config"]["enquiryPeriodRegulation"]),
                tender=tender,
                working_days=self.working_days_config["enquiryPeriodRegulation"],
            ).isoformat()

        if tender["config"]["clarificationUntilDuration"] > 0:
            tender["enquiryPeriod"]["clarificationsUntil"] = calculate_tender_full_date(
                dt_from_iso(tender["enquiryPeriod"]["endDate"]),
                timedelta(days=tender["config"]["clarificationUntilDuration"]),
                tender=tender,
                working_days=self.working_days_config["clarificationUntilDuration"],
            ).isoformat()

    def validate_enquiry_period(self, tender):
        period = tender.get("enquiryPeriod", {})
        if not period:
            return

        if tender["config"]["hasEnquiries"] is False:
            if tender["config"]["enquiryPeriodRegulation"] == 0:
                raise_operation_error(
                    get_request(),
                    "Rogue field",
                    status=422,
                    location="body",
                    name="enquiryPeriod",
                )
            else:
                # do not validate enquiry period
                # it is autogenerated by the system in this case
                return

        start_date = period.get("startDate")
        end_date = period.get("endDate")
        if not start_date or not end_date:
            return

        min_duration = timedelta(days=tender["config"]["minEnquiriesDuration"])
        min_end_date = calculate_tender_full_date(
            parse_date(start_date),
            min_duration,
            tender=tender,
            working_days=self.working_days_config["minEnquiriesDuration"],
        )
        if parse_date(end_date) < min_end_date:
            type = "business" if self.working_days_config["minEnquiriesDuration"] else "calendar"
            raise_operation_error(
                get_request(),
                [
                    "the enquiryPeriod cannot end earlier than {duration.days} full {type} days after the start".format(
                        duration=min_duration, type=type
                    )
                ],
                status=422,
                location="body",
                name="enquiryPeriod",
            )

    def validate_tender_period_start_date(self, data):
        if start_date := data.get("tenderPeriod", {}).get("startDate"):
            if dt_from_iso(start_date) <= get_request_now() - timedelta(minutes=TENDER_PERIOD_START_DATE_STALE_MINUTES):
                raise_operation_error(
                    get_request(),
                    ["tenderPeriod.startDate should be in greater than current date"],
                    status=422,
                    location="body",
                    name="tenderPeriod",
                )

    def validate_tender_period_start_date_change(self, before, after):
        if before["status"] in ("draft", "draft.stage2", "active.enquiries"):
            # still can change tenderPeriod.startDate
            return

        tender_period_start_before = before.get("tenderPeriod", {}).get("startDate")
        tender_period_start_after = after.get("tenderPeriod", {}).get("startDate")
        if tender_period_start_before != tender_period_start_after:
            raise_operation_error(
                get_request(),
                "Can't change tenderPeriod.startDate",
                status=422,
                location="body",
                name="tenderPeriod.startDate",
            )

    def validate_tender_period_duration(self, data):
        if start_date := data.get("tenderPeriod", {}).get("startDate"):
            min_duration = timedelta(days=data["config"]["minTenderingDuration"])
            tender_period_end_date = calculate_tender_full_date(
                parse_date(start_date),
                min_duration,
                tender=data,
                working_days=self.working_days_config["minTenderingDuration"],
                calendar=self.calendar,
            )
            end_date = data.get("tenderPeriod", {}).get("endDate")
            if end_date and tender_period_end_date > parse_date(end_date):
                type = "business" if self.working_days_config["minTenderingDuration"] else "calendar"
                raise_operation_error(
                    get_request(),
                    [
                        "tenderPeriod must be at least {duration.days} full {type} days long".format(
                            duration=min_duration, type=type
                        )
                    ],
                    status=422,
                    location="body",
                    name="tenderPeriod",
                )

    def validate_tender_period_after_enquiry_period(self, data):
        if data["config"]["hasEnquiries"]:
            if data.get("enquiryPeriod") and data["enquiryPeriod"].get("endDate"):
                if data.get("tenderPeriod") and data["tenderPeriod"].get("startDate"):
                    if data["tenderPeriod"]["startDate"] < data["enquiryPeriod"]["endDate"]:
                        raise_operation_error(
                            get_request(),
                            ["period should begin after enquiryPeriod"],
                            status=422,
                            location="body",
                            name="tenderPeriod",
                        )

    def validate_award_criteria_change(self, after, before):
        if before.get("awardCriteria") != after.get("awardCriteria"):
            raise_operation_error(get_request(), "Can't change awardCriteria", name="awardCriteria")

    def validate_kind_change(self, after, before):
        if before["status"] not in ("draft", "draft.stage2"):
            if before["procuringEntity"].get("kind") != after["procuringEntity"].get("kind"):
                raise_operation_error(
                    get_request(),
                    "Can't change procuringEntity.kind in a public tender",
                    status=422,
                    location="body",
                    name="procuringEntity",
                )

    def validate_required_criteria(self, before, after):
        rules = get_criteria_rules(after)

        mpc = after.get("mainProcurementCategory", MainProcurementCategory.SERVICES)

        # Load criteria rules
        required_criteria_ids = set()
        required_article_16_criteria_ids = set()

        for criterion_id, criterion_rules in rules.items():
            if "required" in criterion_rules["rules"]:
                required_criteria_ids.add(criterion_id)
            if "required_services" in criterion_rules["rules"] and mpc == MainProcurementCategory.SERVICES:
                required_criteria_ids.add(criterion_id)
            if "required_works" in criterion_rules["rules"] and mpc == MainProcurementCategory.WORKS:
                required_criteria_ids.add(criterion_id)
            if "required_article_16" in criterion_rules["rules"] and mpc in (
                MainProcurementCategory.WORKS,
                MainProcurementCategory.SERVICES,
            ):
                required_article_16_criteria_ids.add(criterion_id)

        # Gather tender criteria and item criteria
        tender_criteria_ids = set()
        item_criteria_ids = defaultdict(set)
        for criterion in after.get("criteria", ""):
            if criterion.get("classification"):
                tender_criteria_ids.add(criterion["classification"]["id"])
                if criterion.get("relatesTo") == "item":
                    related_item = criterion.get("relatedItem")
                    if related_item:
                        item_criteria_ids[related_item].add(criterion["classification"]["id"])

        # Check required criteria
        required_criteria_ids_diff = required_criteria_ids - tender_criteria_ids
        if required_criteria_ids_diff:
            raise_operation_error(
                get_request(),
                f"Tender must contain all required criteria: {', '.join(sorted(required_criteria_ids_diff))}",
            )

        # Check article 16 criteria if required
        if required_article_16_criteria_ids and not tender_criteria_ids.intersection(required_article_16_criteria_ids):
            raise_operation_error(
                get_request(),
                f"Tender must contain one of article 16 criteria: {', '.join(sorted(required_article_16_criteria_ids))}",
            )

        if tender_created_after(UNIFIED_CRITERIA_LOGIC_FROM) and not self.should_validate_required_market_criteria:
            return

        for item in after.get("items", []):
            market_obj = None
            # get profile/category for each tender criterion
            requirements_from_profile = False
            profile_id = item.get("profile")
            if profile_id:
                profile = get_tender_profile(self.request, profile_id)
                if profile.get("status", "active") == "active":
                    requirements_from_profile = True
                    market_obj = profile
            # check requirements from category only if there is no profile in item or profile is general
            if not requirements_from_profile and (category_id := item.get("category")):
                market_obj = get_tender_category(self.request, category_id)

            # Skip validation if no market object is found
            if not market_obj:
                continue

            # get all criteria ids from market object
            market_criteria_ids = set()
            for market_criterion in market_obj.get("criteria", []):
                classification_id = market_criterion.get("classification", {}).get("id")
                if classification_id:
                    market_criteria_ids.add(classification_id)

            if requirements_from_profile:
                # check if all profile criteria are present for item
                market_criteria_ids_diff = market_criteria_ids - item_criteria_ids[item["id"]]
                if market_criteria_ids_diff:
                    raise_operation_error(
                        get_request(),
                        f"Tender must contain all profile criteria for item {item['id']}: "
                        f"{', '.join(sorted(market_criteria_ids_diff))}",
                    )
            elif not item_criteria_ids[item["id"]].intersection(market_criteria_ids):
                raise_operation_error(
                    get_request(),
                    f"Tender must contain at least one category criteria for item {item['id']}",
                )
            item_criteria_from_market = item_criteria_ids[item["id"]].intersection(
                {CRITERION_TECHNICAL_FEATURES, CRITERION_LOCALIZATION}
            )
            if criteria_diff := item_criteria_from_market.difference(market_criteria_ids):
                raise_operation_error(
                    get_request(),
                    f"Tender contains criteria that don't exist in market object for item {item['id']}: "
                    f"{', '.join(sorted(criteria_diff))}",
                )

    def validate_minimal_step(self, data, before=None):
        """
        Minimal step validation.
        Minimal step should be required if tender has auction

        :param data: tender
        :param before: tender
        :return:
        """
        if not self.tender_has_value:  # arma: no tender.minimalStep
            return
        tender = get_tender()
        has_auction = self.minimal_step_regardless_of_auction or tender["config"]["hasAuction"] is True
        kwargs = {"enabled": has_auction and not tender.get("lots")}
        if not self.minimal_step_required:
            kwargs["required"] = False
        for field in self.minimal_step_fields:
            validate_field(data, field, **kwargs)

    def validate_lot_minimal_step(self, data, before=None):
        """
        Minimal step validation for lot.
        Minimal step should be required if tender has auction

        :param data: lot
        :param before: lot
        :return:
        """
        tender = get_tender()
        kwargs = {
            "enabled": self.minimal_step_regardless_of_auction or tender["config"]["hasAuction"] is True,
        }
        if self.lot_minimal_step_check_before:
            kwargs["before"] = before
        if not self.minimal_step_required:
            kwargs["required"] = False
        for field in self.minimal_step_fields:
            validate_field(data, field, **kwargs)

    def validate_tender_value(self, tender):
        """Validate tender value.

        Validation includes tender value and tender minimal step, if required.

        :param tender: Tender dictionary
        :return: None
        """
        if not self.tender_has_value:  # arma
            return
        has_value_estimation = tender["config"]["hasValueEstimation"]
        tender_value = tender.get("value", {})
        if not tender_value:
            return

        tender_min_step = tender.get("minimalStep", {})
        tender_value_amount = tender_value.get("amount")
        if has_value_estimation is True and tender_value_amount is None:
            raise_operation_error(
                self.request,
                "This field is required",
                status=422,
                location="body",
                name="value.amount",
            )

        if has_value_estimation is False and tender_value_amount:
            raise_operation_error(
                self.request,
                "Rogue field",
                status=422,
                location="body",
                name="value.amount",
            )

        if tender_min_step and tender_value["currency"] != tender_min_step["currency"]:
            raise_operation_error(
                get_request(),
                "Tender minimal step currency should be identical to tender currency",
                status=422,
                location="body",
                name="minimalStep.currency",
            )

        if tender_min_step and tender_value["valueAddedTaxIncluded"] != tender_min_step["valueAddedTaxIncluded"]:
            raise_operation_error(
                get_request(),
                "Tender minimal step valueAddedTaxIncluded should be identical to tender valueAddedTaxIncluded",
                status=422,
                location="body",
                name="minimalStep.valueAddedTaxIncluded",
            )

        # CS-21518 - for some tenders we need to validate that tender has valueAddedTaxIncluded False
        if self.should_validate_vat_not_included:
            validate_value_vat_disabled(self.request, tender_value, "value", self.vat_not_included_validation_from)

        tender_min_step_amount = tender_min_step.get("amount")

        if tender_min_step_amount is None:
            return

        if tender.get("lots"):
            return

        if has_value_estimation and tender_value_amount is not None and tender_value_amount < tender_min_step_amount:
            raise_operation_error(
                get_request(),
                "Tender minimal step amount should be less than tender amount",
                status=422,
                location="body",
                name="minimalStep.amount",
            )

        if has_value_estimation and tender_value_amount is not None:
            self.validate_minimal_step_limits(tender, tender_value_amount, tender_min_step_amount)

    def validate_submission_method(self, data, before=None):
        if not self.submission_method_required:  # competitiveDialogue stage 1
            validate_field(data, "submissionMethod", required=False)
            validate_field(data, "submissionMethodDetails", required=False)
            validate_field(data, "submissionMethodDetails_en", required=False)
            validate_field(data, "submissionMethodDetails_ru", required=False)
            return
        kwargs = {
            "before": before,
            "enabled": data["config"]["hasAuction"] is True,
        }
        validate_field(data, "submissionMethod", default="electronicAuction", **kwargs)
        validate_field(data, "submissionMethodDetails", required=False, **kwargs)
        validate_field(data, "submissionMethodDetails_en", required=False, **kwargs)
        validate_field(data, "submissionMethodDetails_ru", required=False, **kwargs)

    @staticmethod
    def default_procurement_method(data):
        if data["config"]["hasPreSelectionAgreement"] is True:
            return PROCUREMENT_METHOD_SELECTIVE
        if data["procurementMethodType"] in SELECTIVE_PROCUREMENT_METHOD_TYPES:
            return PROCUREMENT_METHOD_SELECTIVE
        if data["procurementMethodType"] in LIMITED_PROCUREMENT_METHOD_TYPES:
            return PROCUREMENT_METHOD_LIMITED
        return PROCUREMENT_METHOD_OPEN

    def validate_procurement_method(self, data, before=None):
        default_procurement_method = self.default_procurement_method(data)
        if before is None and data.get("procurementMethod") is None:
            # default on post only
            data["procurementMethod"] = default_procurement_method
        if data.get("procurementMethod") != default_procurement_method:
            raise_operation_error(
                self.request,
                "procurementMethod should be {}".format(default_procurement_method),
                status=422,
                location="body",
                name="procurementMethod",
            )

    @classmethod
    def tender_items_may_have_different_cpv(cls, tender):
        return tender.get("mainProcurementCategory") in (
            MainProcurementCategory.SERVICES,
            MainProcurementCategory.WORKS,
        ) and tender_created_after(TENDER_ITEMS_DIFFERENT_CPV_FROM, tender)

    def validate_items_classification_prefix(self, tender):
        if not self.should_validate_cpv_prefix:
            return

        classifications = [item["classification"] for item in tender.get("items", "")]

        if not classifications:
            return

        if self.should_validate_items_classifications_prefix and not self.tender_items_may_have_different_cpv(tender):
            validate_items_classifications_prefixes(classifications)

        if not self.should_validate_pre_selection_agreement:
            return

        agreements = tender.get("agreements")

        if not agreements:
            return

        agreement = get_object("agreement")

        if not agreement:
            return

        validate_items_classifications_prefixes(
            classifications,
            root_classification=agreement["classification"],
            root_name="agreement",
            default_prefix_length=CPV_GROUP_PREFIX_LENGTH,
        )

    def validate_items_with_agreement(self, tender):
        """
        Validate items in tender is subset of items in agreement
        """
        COMPARE_FIELDS = (
            "description",
            "classification.scheme",
            "classification.id",
            "unit.code",
        )

        agreement = get_object("agreement")
        if not agreement or not agreement.get("items"):
            return

        def get_field_value(item, field):
            value = item
            for key in field.split("."):
                value = value.get(key, {})
            return value if not isinstance(value, dict) else None

        agreement_field_values = {
            field: {get_field_value(item, field) for item in agreement["items"]} for field in COMPARE_FIELDS
        }

        # Validate each tender item field is in agreement items
        for item in tender.get("items", []):
            for field in COMPARE_FIELDS:
                tender_value = get_field_value(item, field)
                if tender_value and tender_value not in agreement_field_values[field]:
                    raise_operation_error(
                        self.request,
                        f"Item {field} '{tender_value}' not found in agreement items",
                        status=422,
                        name="items",
                    )

        # Validate field combinations exist in agreement
        tender_combinations = {
            tuple(get_field_value(item, field) for field in COMPARE_FIELDS) for item in tender.get("items", [])
        }

        agreement_combinations = {
            tuple(get_field_value(item, field) for field in COMPARE_FIELDS) for item in agreement["items"]
        }

        invalid_combinations = tender_combinations - agreement_combinations
        if invalid_combinations:
            invalid_item = next(iter(invalid_combinations))
            raise_operation_error(
                self.request,
                "Item not found in agreement items: {}".format(invalid_item),
                status=422,
                name="items",
            )

    @classmethod
    def validate_items_classification_prefix_unchanged(cls, before, after):
        if cls.tender_items_may_have_different_cpv(after):
            return
        prefix_list = set()
        for item in before.get("items", ""):
            prefix_list.add(item["classification"]["id"][:CPV_GROUP_PREFIX_LENGTH])
        for item in after.get("items", ""):
            prefix_list.add(item["classification"]["id"][:CPV_GROUP_PREFIX_LENGTH])
        if len(prefix_list) != 1:
            prefix_name = CPV_PREFIX_LENGTH_TO_NAME[CPV_GROUP_PREFIX_LENGTH]
            raise_operation_error(
                get_request(),
                [f"Can't change classification {prefix_name} of items"],
                status=422,
                name="items",
            )

    def validate_tender_period_extension(self, tender):
        if not self.tender_period_extension_check:
            return
        if "tenderPeriod" in tender and "endDate" in tender["tenderPeriod"]:
            tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
            if (
                calculate_tender_full_date(
                    get_request_now(),
                    self.tender_period_extra,
                    tender=tender,
                    working_days=self.tender_period_extra_working_days,
                )
                > tendering_end
            ):
                raise_operation_error(
                    get_request(),
                    "tenderPeriod should be extended by {0.days} {1}".format(
                        self.tender_period_extra,
                        "working days" if self.tender_period_extra_working_days else "days",
                    ),
                )

    def validate_docs(self, data, before=None):
        documents = data.get("documents", [])
        if before and len(before.get("documents", [])) != len(documents) or before is None:
            if tender_created_after(NOTICE_DOC_REQUIRED_FROM):
                validate_doc_type_quantity(documents)
            if tender_created_after(EVALUATION_REPORTS_DOC_REQUIRED_FROM):
                validate_doc_type_quantity(documents, document_type="evaluationReports")
        self.validate_tender_docs_confidentiality(documents)

    def validate_tender_docs_confidentiality(self, documents):
        for doc in documents:
            validate_edrpou_confidentiality_doc(doc, should_be_public=self.all_documents_should_be_public)

    @staticmethod
    def calculate_item_identification_tuple(item):
        result = (
            item["id"],
            item["classification"]["id"],
            item["classification"]["scheme"],
            item["unit"]["code"] if item.get("unit") else None,
            tuple((c["id"], c["scheme"]) for c in item.get("additionalClassifications", "")),
        )
        return result

    @classmethod
    def is_agreement_not_active(cls, agreement):
        return agreement.get("status") != "active"

    def has_insufficient_active_contracts(self, agreement):
        active_contracts_count = sum(c["status"] == "active" for c in agreement.get("contracts", ""))
        return active_contracts_count < self.agreement_min_active_contracts

    def has_mismatched_procuring_entities(self, tender, agreement):
        if not self.should_match_agreement_procuring_entity:
            return False
        if (
            self.agreement_procuring_entity_match_except_defense
            and tender["procuringEntity"]["kind"] == ProcuringEntityKind.DEFENSE
            and agreement["procuringEntity"]["kind"] == ProcuringEntityKind.DEFENSE
        ):
            # Defense procuring entity can use agreement with other defense procuring entity
            return False

        agreement_identifier = agreement["procuringEntity"]["identifier"]
        tender_identifier = tender["procuringEntity"]["identifier"]
        return (
            tender_identifier["id"] != agreement_identifier["id"]
            or tender_identifier["scheme"] != agreement_identifier["scheme"]
        )

    def validate_related_lot_in_items(self, after):
        if (
            tender_created_after(RELATED_LOT_REQUIRED_FROM)
            or after.get("procurementMethodType") in [ABOVE_THRESHOLD, COMPETITIVE_ORDERING]
        ) and after["status"] != "draft":
            for item in after["items"]:
                if not item.get("relatedLot"):
                    raise_operation_error(
                        get_request(),
                        "This field is required",
                        status=422,
                        location="body",
                        name="item.relatedLot",
                    )

    def update_complaint_period(self, tender):
        if tender["config"]["hasTenderComplaints"] is not True:
            return
        if "tenderPeriod" not in tender or "endDate" not in tender["tenderPeriod"]:
            return
        if tender["config"]["tenderComplainRegulation"] == 0:
            return
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_tender_full_date(
            tendering_end,
            -timedelta(days=tender["config"]["tenderComplainRegulation"]),
            tender=tender,
            working_days=self.working_days_config["tenderComplainRegulation"],
        )
        tender["complaintPeriod"] = {
            "startDate": tender["tenderPeriod"]["startDate"],
            "endDate": end_date.isoformat(),
        }

    def validate_remove_inspector(self, before, after):
        if after["status"] == "draft":
            return
        if before.get("inspector") and not after.get("inspector"):
            raise_operation_error(
                get_request(),
                f"You can't remove inspector in current({after['status']}) tender status",
                status=422,
            )

    def validate_change_item_profile_or_category(self, after: dict, before: dict, force_validate: bool = False) -> None:
        if not self.item_profile_category_check_on_post and self.request.method == "POST":
            return
        after_cp = {}
        for item in after.get("items", []):
            after_cp[item["id"]] = {
                "profile": item.get("profile"),
                "category": item.get("category"),
            }

        before_cp = {}
        for item in before.get("items", []):
            before_cp[item["id"]] = {
                "profile": item.get("profile"),
                "category": item.get("category"),
            }

        request = get_request()

        for k, after_values in after_cp.items():
            before_values = before_cp.get(k, {})
            is_profile_changed = before_values.get("profile") != after_values.get("profile")
            is_category_changed = before_values.get("category") != after_values.get("category")

            if is_profile_changed or is_category_changed or force_validate:
                if (category_id := after_values.get("category")) is not None:
                    get_tender_category(request, category_id, ("active",))

                if (profile_id := after_values.get("profile")) is not None:
                    profile = get_tender_profile(request, profile_id, ("active",))

                    if profile.get("relatedCategory") != category_id:
                        raise_operation_error(request, "Profile should be related to category", status=422)

            if (is_profile_changed or is_category_changed) and before:
                self.cancel_all_technical_criteria(before, after, k)

    def cancel_all_technical_criteria(self, before_tender: dict, after_tender: dict, item_id: str) -> None:
        criteria_ids = (CRITERION_TECHNICAL_FEATURES, CRITERION_LOCALIZATION)
        now = get_request_now()
        for criterion in after_tender.get("criteria", []):
            if (
                criterion.get("classification", {}).get("id") in criteria_ids
                and criterion.get("relatedItem") == item_id
            ):
                # get requirement ids from criterion before patch just to cancel only existed ones
                before_requirements_ids = [
                    req["id"]
                    for before_criterion in before_tender.get("criteria", [])
                    if before_criterion["id"] == criterion["id"]
                    for rg in before_criterion.get("requirementGroups", [])
                    for req in rg.get("requirements", [])
                ]
                for rg in criterion.get("requirementGroups", ""):
                    for req in rg.get("requirements", ""):
                        if req.get("id") in before_requirements_ids:
                            req["status"] = ReqStatuses.CANCELLED
                            req["dateModified"] = now.isoformat()

    def validate_main_procurement_category(self, tender):
        value = tender.get("mainProcurementCategory")
        if value is None and self.main_procurement_category_required and tender_created_after(MPC_REQUIRED_FROM):
            raise_operation_error(self.request, ["This field is required."], status=422, name="mainProcurementCategory")
        if value is not None and value not in self.main_procurement_category_choices:
            raise_operation_error(
                self.request,
                [f"Value must be one of {list(self.main_procurement_category_choices)}."],
                status=422,
                name="mainProcurementCategory",
            )

    def validate_award_criteria(self, tender, on_post=False):
        if self.award_criteria_choices is None:
            return
        if on_post and tender.get("awardCriteria") is None and self.award_criteria_default:
            tender["awardCriteria"] = self.award_criteria_default
        value = tender.get("awardCriteria")
        if (
            self.award_criteria_lcc_features_check
            and value == AWARD_CRITERIA_LIFE_CYCLE_COST
            and tender.get("features")
        ):
            raise_operation_error(
                self.request,
                [f"Can`t add features with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria"],
                status=422,
                name="awardCriteria",
            )
        if value is not None and value not in self.award_criteria_choices:
            raise_operation_error(
                self.request,
                [f"Value must be one of {list(self.award_criteria_choices)}."],
                status=422,
                name="awardCriteria",
            )

    def validate_contract_template_name_allowed(self, tender):
        if tender.get("contractTemplateName") is not None and (
            not self.contract_template_name_allowed or self.tender_items_may_have_different_cpv(tender)
        ):
            raise_operation_error(self.request, "Rogue field", status=422, name="contractTemplateName")

    def validate_items_related_lot_allowed(self, tender):
        if self.items_related_lot_error is None:
            return
        errors = [
            {"relatedLot": [self.items_related_lot_error]}
            for item in tender.get("items") or []
            if item.get("relatedLot")
        ]
        if errors:
            raise_operation_error(self.request, errors, status=422, name="items")

    def validate_items_classification_id(self, tender, on_post=False):
        if on_post and not self.items_classification_id_check_on_post:
            return
        if self.items_classification_id_check:
            validate_items_classification_id(self.request, tender.get("items"))

    def validate_tender_milestones_required(self, tender, on_post=False):
        delivery_financing = self.milestones_delivery_financing_required
        if on_post and not self.milestones_delivery_financing_required_on_post:
            delivery_financing = False
        validate_tender_milestones_required(
            self.request,
            tender,
            required=self.milestones_required,
            delivery_financing=delivery_financing,
        )

    def validate_procuring_entity_required_fields(self, tender):
        if self.procuring_entity_required_fields and tender.get("procuringEntity") is not None:
            validate_required_nested_fields(
                self.request, tender, {"procuringEntity": self.procuring_entity_required_fields}
            )

    def validate_items_required_fields(self, tender):
        validate_items_required_fields(
            self.request,
            tender.get("items"),
            delivery=self.items_delivery_required,
            unit=self.items_unit_required,
            quantity=self.items_quantity_required,
        )

    def validate_multilingual_fields(self, tender):
        if self.required_multilingual_fields:
            validate_required_nested_fields(self.request, tender, self.required_multilingual_fields)

    def set_procuring_entity_available_language(self, tender):
        default = self.procuring_entity_available_language_default
        if not default:
            return
        procuring_entity = tender.get("procuringEntity") or {}
        contact_points = [procuring_entity.get("contactPoint")] + (
            procuring_entity.get("additionalContactPoints") or []
        )
        for contact_point in contact_points:
            if contact_point is not None and contact_point.get("availableLanguage") is None:
                contact_point["availableLanguage"] = default

    def validate_features(self, tender):
        features = tender.get("features")
        if not features:
            return
        max_weight = self.features_max_weight
        # Decimal comparison: values may be floats or Decimals (CFA), and Decimal("0.3") > 0.3
        max_weight_decimal = Decimal(str(max_weight))
        # same shape/message as FloatType(max_value=...) used to produce on the model
        errors = []
        for feature in features:
            enum_errors = [
                {"value": [f"Float value should be less than {max_weight}."]}
                for enum in feature.get("enum") or []
                if enum.get("value") is not None and Decimal(str(enum["value"])) > max_weight_decimal
            ]
            if enum_errors:
                errors.append({"enum": enum_errors})
        if errors:
            raise_operation_error(self.request, errors, status=422, name="features")
        try:
            validate_features_custom_weight(tender, features, max_weight_decimal)
        except ValidationError as e:
            raise_operation_error(self.request, e.messages, status=422, name="features")

    def validate_patch_status_choice(self, before, after):
        choices = self.patch_status_choices
        if choices is None or after.get("status") == before.get("status"):
            return
        if after.get("status") not in choices:
            raise_operation_error(self.request, [f"Value must be one of {list(choices)}."], status=422, name="status")

    def validate_enquiry_period_required(self, tender, on_post=False):
        if not self.enquiry_period_required:
            return
        period = tender.get("enquiryPeriod")
        if period is None:
            raise_operation_error(self.request, ["This field is required."], status=422, name="enquiryPeriod")
        if not period.get("endDate"):
            raise_operation_error(
                self.request, {"endDate": ["This field is required."]}, status=422, name="enquiryPeriod"
            )
        if on_post and not period.get("startDate"):
            period["startDate"] = get_request_now().isoformat()

    def validate_tender_period_start_date_required(self, tender, on_post=False):
        if not self.tender_period_start_date_required:
            return
        period = tender.get("tenderPeriod")
        if period is None or period.get("startDate"):
            return
        if on_post:
            period["startDate"] = get_request_now().isoformat()
        else:
            raise_operation_error(
                self.request, {"startDate": ["This field is required."]}, status=422, name="tenderPeriod"
            )

    def validate_items_profile(self, tender):
        if not self.items_profile_required:
            return None
        required_profile_for_tender = (
            tender.get("value", {}).get("amount", 0) >= PROFILE_REQUIRED_MIN_VALUE_AMOUNT
            and tender.get("value", {}).get("currency") == "UAH"
            and tender.get("procuringEntity", {}).get("kind")
            not in (ProcuringEntityKind.SPECIAL, ProcuringEntityKind.DEFENSE, ProcuringEntityKind.OTHER)
        )
        for item in tender["items"]:
            med_category_used = False
            if category_id := item.get("category"):
                category = get_tender_category(self.request, category_id)
                med_category_used = category.get("classification", {}).get("id", "").startswith(CPV_PHARM_PREFIX)
            else:
                raise_operation_error(
                    self.request,
                    [{"category": ["This field is required."]}],
                    status=422,
                    name="items",
                )
            if (required_profile_for_tender or med_category_used) and not item.get("profile"):
                raise_operation_error(
                    self.request,
                    [{"profile": ["This field is required."]}],
                    status=422,
                    name="items",
                )

    def validate_items_quantity(self, data):
        if tender_created_before(ITEM_QUANTITY_REQUIRED_FROM):
            return

        items_with_quantity = defaultdict(lambda: [])
        for item in data.get("items", []):
            lot = item.get("relatedLot")
            items_with_quantity.setdefault(lot, [])
            if item.get("quantity") not in (None, 0):
                items_with_quantity[lot].append(item)
        for lot_id, not_empty_items in items_with_quantity.items():
            if not not_empty_items:
                raise_operation_error(
                    self.request,
                    f"At least one item should be with not empty quantity{' for each lot' if lot_id is not None else ''}",
                    status=422,
                    name="items",
                )

    def validate_contract_template_name(self, after, before):
        def raise_contract_template_name_error(message):
            raise_operation_error(
                self.request,
                message,
                status=422,
                location="body",
                name="contractTemplateName",
            )

        # Get tender status
        tender_before_status = before.get("status", "draft")
        tender_after_status = after.get("status", "draft")

        # Find if contractTemplateName is changed
        contract_template_name_before = before.get("contractTemplateName")
        contract_template_name = after.get("contractTemplateName")
        contract_template_name_changed = contract_template_name != contract_template_name_before

        # Check if contractTemplateName is allowed to be changed
        if contract_template_name_changed and not self.contract_template_name_patch_statuses:
            raise_contract_template_name_error("Rogue field")

        # Check if contractTemplateName is allowed to be changed in current tender status
        if contract_template_name_changed and tender_before_status not in self.contract_template_name_patch_statuses:
            raise_contract_template_name_error(
                f"Can't change contract template name in current tender '{tender_before_status}' status"
            )

        # Get all classification IDs from items
        classification_ids = set()
        for item in after.get("items", []):
            if item.get("classification") and item["classification"].get("id"):
                classification_ids.add(item["classification"]["id"])

        # Find if contractProforma is present
        tender_documents = after.get("documents", "")
        has_contract_proforma = any(i.get("documentType", "") == "contractProforma" for i in tender_documents)

        # Check if both contractTemplateName and contractProforma are present simultaneously
        if has_contract_proforma and contract_template_name:
            raise_contract_template_name_error(
                "Cannot use both contractTemplateName and contractProforma document simultaneously",
            )

        # Check if contractTemplateName or contractProforma is required
        if tender_after_status not in ("draft",) and self.contract_template_required:
            # FIXME: next if statement is temporary fix for already active tenders without contract template
            # TODO: remove this if later
            if tender_before_status in ("draft",) or contract_template_name_changed:
                # Check if either contractTemplateName or contractProforma is present
                if not has_contract_proforma and not contract_template_name:
                    raise_contract_template_name_error(
                        "Either contractTemplateName or contractProforma document is required"
                    )

        # If contractTemplateName is not specified, no further checks needed
        if not contract_template_name:
            return

        # Check if classifications is missing
        if not classification_ids:
            raise_contract_template_name_error("Can't set contractTemplateName for tender without classification")

        # Get expected template names for the classifications
        expected_template_names = get_contract_template_names_for_classification_ids(
            classification_ids,
            active_only=contract_template_name_changed,  # if unchanged - allow inactive templates
        )

        # Check if contractTemplateName is forbidden for excluded classifications
        if not expected_template_names:
            raise_contract_template_name_error(
                f"contractTemplateName is not allowed for current classifications {', '.join(sorted(classification_ids))}"
            )

        # Check if contractTemplateName is correct for the current classifications
        if contract_template_name not in expected_template_names:
            raise_contract_template_name_error(
                f"Incorrect contractTemplateName {contract_template_name} "
                f"for current classifications {', '.join(sorted(classification_ids))}, "
                f"use one of {', '.join(sorted(expected_template_names))}",
            )

    def set_contract_change_rationale_types(self, data):
        if tender_created_before(CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM):
            return
        mapping = CAUSE_TO_RATIONALE_TYPES_MAPPING
        rationale_types_reference = get_change_rationale_types_reference(data, mapping)
        data["contractChangeRationaleTypes"] = rationale_types_reference


class TenderDetailsMixing(TenderConfigMixin, BaseTenderDetailsMixing):
    pass


class TenderDetailsState(TenderDetailsMixing, TenderState):
    pass
