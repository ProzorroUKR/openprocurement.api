from copy import deepcopy
from datetime import timedelta
from logging import getLogger

from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.constants_env import (
    CRITERIA_CLASSIFICATION_UNIQ_FROM,
    UNIFIED_CRITERIA_LOGIC_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_agreement, get_tender
from openprocurement.api.utils import (
    get_agreement_by_id,
    get_tender_by_id,
    handle_data_exceptions,
    raise_operation_error,
)
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.serializers.agreement import (
    AgreementSerializer,
)
from openprocurement.tender.cfaselectionua.constants import (
    MIN_ACTIVE_CONTRACTS,
    MIN_PERIOD_UNTIL_AGREEMENT_END,
    MINIMAL_STEP_PERCENTAGE,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.cfaselectionua.procedure.models.agreement import (
    PatchAgreement,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.constants import (
    AGREEMENT_CHANGE_MESSAGE,
    AGREEMENT_CONTRACTS_MESSAGE,
    AGREEMENT_EXPIRED_MESSAGE,
    AGREEMENT_IDENTIFIER_MESSAGE,
    AGREEMENT_ITEMS_MESSAGE,
    AGREEMENT_NOT_FOUND_MESSAGE,
    AGREEMENT_START_DATE_MESSAGE,
    AGREEMENT_STATUS_MESSAGE,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    tender_created_after,
    validate_field,
)
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)
from openprocurement.tender.core.utils import (
    calculate_tender_date,
    calculate_tender_full_date,
)

LOGGER = getLogger(__name__)


class CFASelectionTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    agreement_min_active_contracts = MIN_ACTIVE_CONTRACTS
    agreement_min_period_until_end = MIN_PERIOD_UNTIL_AGREEMENT_END
    agreement_allowed_types = [CFA_UA]

    should_validate_pre_selection_agreement = False

    working_days_config = WORKING_DAYS_CONFIG

    contract_template_name_patch_statuses = ("draft", "active.enquiries", "active.tendering")

    def on_post(self, tender):
        super().on_post(tender)
        self.check_owner_forbidden_fields(tender)

    def on_patch(self, before, after):
        if before.get("procuringEntity") != after.get("procuringEntity"):
            self._validate_procurement_entity_kind(after)
        self.validate_contract_template_name(after, before)
        self.validate_tender_period_duration(after)
        self.validate_tender_period_after_enquiry_period(after)
        self.validate_tender_period_start_date_change(before, after)
        if get_request().authenticated_role == "agreement_selection":
            if after["status"] == "active.enquiries":
                agreement = after["agreements"][0]
                reason = self.find_agreement_unsuccessful_reason(after, agreement)
                if reason:
                    after["unsuccessfulReason"] = [reason]
                    self.get_change_tender_status_handler("draft.unsuccessful")(after)

                else:
                    self.update_periods(after)

                    calculate_agreement_contracts_value_amount(after)

                    minimal_step = deepcopy(after["lots"][0]["value"])
                    minimal_step["amount"] = round(MINIMAL_STEP_PERCENTAGE * minimal_step["amount"], 2)
                    after["lots"][0]["minimalStep"] = minimal_step

                    calculate_tender_features(after)
            elif after["status"] == "draft.unsuccessful":
                after["unsuccessfulReason"] = [AGREEMENT_NOT_FOUND_MESSAGE]
                self.get_change_tender_status_handler("draft.unsuccessful")(after)
            elif before["status"] != "draft.pending" or after["status"] != "draft.pending":
                raise_operation_error(
                    get_request(),
                    f"Can't switch tender from ({before['status']}) to ({after['status']}) status.",
                )

        else:  # tender owner
            self.check_owner_forbidden_fields(after)

            if before["status"] == "draft" and after["status"] == "draft":
                pass
            elif before["status"] == "draft" and after["status"] == "draft.pending":
                self.update_periods(after)
                if not after["agreements"] or not after.get("items"):
                    raise_operation_error(
                        get_request(),
                        "Can't switch tender to (draft.pending) status without agreements or items.",
                    )
                self.validate_exist_guarantee_criteria(after)
                self.validate_required_criteria(before, after)
                self.validate_criteria_requirement_from_market(after.get("criteria", []))

            elif before["status"] != after["status"]:
                raise_operation_error(
                    get_request(),
                    f"Can't switch tender from ({before['status']}) to ({after['status']}) status.",
                )

            elif after["status"] == "active.enquiries":
                if len(before["items"]) != len(after["items"]):
                    raise_operation_error(get_request(), "Can't update tender items. Items count mismatch")

                if [item["id"] for item in before["items"]] != [item["id"] for item in after["items"]]:
                    raise_operation_error(get_request(), "Can't update tender items. Items order mismatch")

                for f in ("unit", "classification", "additionalClassifications"):
                    if [item.get(f) for item in before["items"]] != [item.get(f) for item in after["items"]]:
                        raise_operation_error(
                            get_request(),
                            f"Can't update {f} in items in active.enquiries",
                        )

                if before["tenderPeriod"]["startDate"] != after["tenderPeriod"].get("startDate"):
                    raise_operation_error(
                        get_request(),
                        "Can't update tenderPeriod.startDate in active.enquiries",
                    )

                if before["procuringEntity"] != after["procuringEntity"]:
                    raise_operation_error(
                        get_request(),
                        "Can't update procuringEntity in active.enquiries",
                    )

                if "items" in get_request().validated["json_data"]:
                    calculate_agreement_contracts_value_amount(after)
            else:
                allowed_fields = ("procurementMethodDetails", "contractTemplateName")
                for k in get_request().validated["json_data"].keys():
                    if k not in allowed_fields:
                        if before.get(k) != after.get(k):
                            raise_operation_error(
                                get_request(),
                                f"Only fields {allowed_fields} can be updated at {after['status']}",
                            )
        if tender_created_after(CRITERIA_CLASSIFICATION_UNIQ_FROM):
            self._validate_criterion_uniq(after.get("criteria", []))
        self.validate_docs(after, before)
        self.always(after)

    def copy_agreement_data(self, tender):
        # TODO: rewrite with direct agreement dict creation
        agreement = get_agreement()
        if agreement:
            agreement_data = AgreementSerializer(agreement).data
            agreement_data.pop("id")
            agreement_data.pop("documents", None)
            agreement_data.pop("agreementType", None)
            with handle_data_exceptions(get_request()):
                tender_agreement = PatchAgreement(agreement_data).serialize()
            tender["agreements"][0].update(tender_agreement)
            return tender["agreements"][0]

    def update_periods(self, tender):
        enquiry_end = calculate_tender_full_date(
            get_request_now(),
            timedelta(days=tender["config"]["minEnquiriesDuration"]),
            working_days=self.working_days_config["minEnquiriesDuration"],
            tender=tender,
        )
        tender["enquiryPeriod"] = {
            "startDate": get_request_now().isoformat(),
            "endDate": enquiry_end.isoformat(),
        }
        tender_end = calculate_tender_full_date(
            enquiry_end,
            timedelta(days=tender["config"]["minTenderingDuration"]),
            working_days=self.working_days_config["minTenderingDuration"],
            tender=tender,
        )
        tender["tenderPeriod"] = {
            "startDate": tender["enquiryPeriod"]["endDate"],
            "endDate": tender_end.isoformat(),
        }

    @staticmethod
    def watch_value_meta_changes(tender):
        pass  # TODO: shouldn't it work here

    def find_agreement_unsuccessful_reason(self, tender, agreement):
        if self.is_agreement_not_active(agreement):
            return AGREEMENT_STATUS_MESSAGE

        if self.are_tender_items_is_not_subset_of_agreement_items(tender, agreement):
            return AGREEMENT_ITEMS_MESSAGE

        if self.is_agreement_expired(tender, agreement):
            return AGREEMENT_EXPIRED_MESSAGE.format(self.agreement_min_period_until_end.days)

        elif self.is_agreement_start_date_later(tender, agreement):
            return AGREEMENT_START_DATE_MESSAGE

        if self.is_agreement_has_pending_changes(agreement):
            return AGREEMENT_CHANGE_MESSAGE

        if self.has_insufficient_active_contracts(agreement):
            return AGREEMENT_CONTRACTS_MESSAGE.format(self.agreement_min_active_contracts)

        if self.has_mismatched_procuring_entities(tender, agreement):
            return AGREEMENT_IDENTIFIER_MESSAGE

    @classmethod
    def are_tender_items_is_not_subset_of_agreement_items(cls, tender, agreement):
        agreement_items_ids = {
            cls.calculate_item_identification_tuple(agreement_item) for agreement_item in agreement.get("items", "")
        }
        tender_items_ids = {
            cls.calculate_item_identification_tuple(tender_item) for tender_item in tender.get("items", "")
        }
        return not tender_items_ids.issubset(agreement_items_ids)

    @classmethod
    def is_agreement_expired(cls, tender, agreement):
        agreement_expire_date = calculate_tender_date(
            dt_from_iso(agreement["period"]["endDate"]),
            -cls.agreement_min_period_until_end,
            tender=tender,
        )
        return get_request_now() > agreement_expire_date

    @classmethod
    def is_agreement_start_date_later(cls, tender, agreement):
        return agreement["period"]["startDate"] > tender["date"]

    @classmethod
    def is_agreement_has_pending_changes(cls, agreement):
        for change in agreement.get("changes", ""):
            if change["status"] == "pending":
                return True
        return False

    @staticmethod
    def check_owner_forbidden_fields(tender):
        if tender["status"] in ("draft", "draft.pending"):
            if "features" in tender:
                raise_operation_error(get_request(), "Can't add features")

    def validate_minimal_step(self, data, before=None):
        """
        Override to skip minimalStep required validation.
        It's not required for cfaselectionua in tender level.
        In cfaselectionua during setting status to active.enquiries
        field `minimalStep` is calculated using particular formula.

        :param data: tender or lot
        :param before: tender or lot
        :return:
        """
        tender = get_tender()
        kwargs = {
            "enabled": tender["config"]["hasAuction"] is True and not tender.get("lots"),
        }
        validate_field(data, "minimalStep", required=False, **kwargs)

    def validate_lot_minimal_step(self, data, before=None):
        """
        Minimal step validation for lot.
        Minimal step should be required if tender has auction
        In cfaselectionua during setting status to active.enquiries
        field `minimalStep` for lots is calculated using particular formula.

        :param data: lot
        :param before: lot
        :return:
        """
        tender = get_tender()
        kwargs = {
            "before": before,
            "enabled": tender["config"]["hasAuction"] is True,
        }
        validate_field(data, "minimalStep", required=False, **kwargs)

    def validate_tender_period_extension(self, tender):
        pass

    def validate_tender_docs_confidentiality(self, documents):
        for doc in documents:
            validate_edrpou_confidentiality_doc(doc, should_be_public=True)

    def validate_exist_guarantee_criteria(self, tender):
        if tender_created_after(UNIFIED_CRITERIA_LOGIC_FROM):
            return

        agreement_id = tender["agreements"][0]["id"]
        if not (agreement := get_agreement_by_id(get_request(), agreement_id, raise_error=False)):
            return

        if not (cfaua_tender := get_tender_by_id(get_request(), agreement["tender_id"], raise_error=False)):
            return

        if not (criterion_for_check := get_guarantee_criterion(tender)):
            return

        if not (needed_criterion := get_guarantee_criterion(cfaua_tender)):
            raise_operation_error(
                get_request(),
                "CRITERION.OTHER.CONTRACT.GUARANTEE criterion is forbidden",
            )

        clean_criteria(needed_criterion)
        clean_criteria(criterion_for_check)

        if needed_criterion != criterion_for_check:
            raise_operation_error(
                get_request(),
                "CRITERION.OTHER.CONTRACT.GUARANTEE should be identical to criterion in cfaua",
            )

    @staticmethod
    def set_lot_value(tender: dict, data: dict) -> None:
        pass

    @staticmethod
    def set_lot_minimal_step(tender: dict, data: dict) -> None:
        pass


class CFASelectionTenderDetailsState(CFASelectionTenderDetailsMixing, CFASelectionTenderState):
    pass


def calculate_agreement_contracts_value_amount(tender):
    agreement = tender["agreements"][0]
    tender_items = {i["id"]: i["quantity"] for i in tender.get("items", "")}
    for contract in agreement.get("contracts", ""):
        contract["value"] = {
            "amount": 0,
            "currency": contract["unitPrices"][0]["value"]["currency"],
            "valueAddedTaxIncluded": contract["unitPrices"][0]["value"]["valueAddedTaxIncluded"],
        }

        for unitPrice in contract.get("unitPrices", ""):
            if unitPrice.get("relatedItem") in tender_items:
                contract["value"]["amount"] += unitPrice["value"]["amount"] * tender_items[unitPrice["relatedItem"]]

        contract["value"]["amount"] = round(contract["value"]["amount"], 2)

    contract_values = [contract["value"] for contract in agreement.get("contracts", "")]
    if contract_values:
        tender["value"] = tender["lots"][0]["value"] = value = max(contract_values, key=lambda value: value["amount"])

        # handle minimalStep auto decrease
        minimal_step = tender["lots"][0].get("minimalStep")
        if minimal_step and minimal_step["amount"] > value["amount"]:
            tender["lots"][0]["minimalStep"] = value


def calculate_tender_features(tender):
    #  calculation tender features after items validation
    agreement_features = tender["agreements"][0].get("features")
    if agreement_features:
        tender_features = []
        tender_items_ids = {i["id"] for i in tender.get("items", "")}

        for feature in agreement_features:
            if feature["featureOf"] == "tenderer":
                tender_features.append(feature)

            elif feature["featureOf"] == "item" and feature.get("relatedItem") in tender_items_ids:
                tender_features.append(feature)

            elif feature["featureOf"] == "lot" and feature.get("relatedItem") == tender["lots"][0]["id"]:
                tender_features.append(feature)

        tender["features"] = tender_features


def get_guarantee_criterion(tender):
    guarantee_clasif_id = "CRITERION.OTHER.CONTRACT.GUARANTEE"
    return deepcopy(
        next(
            (c for c in tender.get("criteria", "") if c.get("classification", {}).get("id") == guarantee_clasif_id),
            None,
        )
    )


def clean_criteria(criterion):
    def remove_fields(data):
        field_for_remove = ("id", "date", "datePublished", "eligibleEvidences")
        for f in field_for_remove:
            data.pop(f, None)

    remove_fields(criterion)
    for rg in criterion.get("requirementGroups", ""):
        remove_fields(rg)
        requirements = rg.get("requirements", "")

        for req in requirements[:]:
            if req.get("status", "active") != "active":
                requirements.remove(req)
                continue

            remove_fields(req)
