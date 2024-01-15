from openprocurement.api.auth import ACCR_5, ACCR_1, ACCR_2
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.core.procedure.context import (
    get_request,
    get_tender_config,
)
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    validate_field,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState
from openprocurement.tender.cfaselectionua.constants import (
    MIN_PERIOD_UNTIL_AGREEMENT_END,
    MIN_ACTIVE_CONTRACTS,
    ENQUIRY_PERIOD,
    TENDERING_DURATION,
    MINIMAL_STEP_PERCENTAGE,
)
from openprocurement.tender.core.constants import (
    AGREEMENT_NOT_FOUND_MESSAGE,
    AGREEMENT_STATUS_MESSAGE,
    AGREEMENT_ITEMS_MESSAGE,
    AGREEMENT_EXPIRED_MESSAGE,
    AGREEMENT_START_DATE_MESSAGE, AGREEMENT_CHANGE_MESSAGE, AGREEMENT_CONTRACTS_MESSAGE, AGREEMENT_IDENTIFIER_MESSAGE,
)
from openprocurement.tender.core.utils import calculate_tender_business_date, calculate_tender_date
from openprocurement.api.utils import raise_operation_error
from copy import deepcopy


class CFASelectionTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (ACCR_1, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_2,)

    agreement_min_active_contracts = MIN_ACTIVE_CONTRACTS
    agreement_min_period_until_end = MIN_PERIOD_UNTIL_AGREEMENT_END

    should_validate_pre_selection_agreement = False

    def on_post(self, tender):
        super().on_post(tender)
        self.check_owner_forbidden_fields(tender)

    def on_patch(self, before, after):
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
                    after["minimalStep"] = after["lots"][0]["minimalStep"] = minimal_step

                    calculate_tender_features(after)
            elif after["status"] == "draft.unsuccessful":
                after["unsuccessfulReason"] = [AGREEMENT_NOT_FOUND_MESSAGE]
                self.get_change_tender_status_handler("draft.unsuccessful")(after)
            elif before["status"] != "draft.pending" or after["status"] != "draft.pending":
                raise_operation_error(
                    get_request(),
                    f"Can't switch tender from ({before['status']}) to ({after['status']}) status."
                )

        else:  # tender owner
            self.check_owner_forbidden_fields(after)
            self.validate_tender_exclusion_criteria(before, after)

            if before["status"] == "draft" and after["status"] == "draft":
                pass
            elif before["status"] == "draft" and after["status"] == "draft.pending":
                self.update_periods(after)
                if not after["agreements"] or not after.get("items"):
                    raise_operation_error(
                        get_request(),
                        "Can't switch tender to (draft.pending) status without agreements or items."
                    )
            elif before["status"] != after["status"]:
                raise_operation_error(
                    get_request(),
                    f"Can't switch tender from ({before['status']}) to ({after['status']}) status."
                )

            elif after["status"] == "active.enquiries":
                if len(before["items"]) != len(after["items"]):
                    raise_operation_error(get_request(), "Can't update tender items. Items count mismatch")

                if [item["id"] for item in before["items"]] != [item["id"] for item in after["items"]]:
                    raise_operation_error(get_request(), "Can't update tender items. Items order mismatch")

                for f in ("unit", "classification", "additionalClassifications"):
                    if [item.get(f) for item in before["items"]] != [item.get(f) for item in after["items"]]:
                        raise_operation_error(get_request(), f"Can't update {f} in items in active.enquiries")

                if before["tenderPeriod"]["startDate"] != after["tenderPeriod"].get("startDate"):
                    raise_operation_error(get_request(), f"Can't update tenderPeriod.startDate in active.enquiries")

                if before["procuringEntity"] != after["procuringEntity"]:
                    raise_operation_error(get_request(), f"Can't update procuringEntity in active.enquiries")

                if "items" in get_request().validated["json_data"]:
                    calculate_agreement_contracts_value_amount(after)
            else:
                for k in get_request().validated["json_data"].keys():
                    if k != "procurementMethodDetails":
                        if before.get(k) != after.get(k):
                            raise_operation_error(get_request(),
                                                  f"Only procurementMethodDetails can be updated at {after['status']}")
        self.always(after)

    @staticmethod
    def update_periods(tender):
        enquiry_end = calculate_tender_business_date(get_now(), ENQUIRY_PERIOD, tender)
        tender["enquiryPeriod"] = {
            "startDate": get_now().isoformat(),
            "endDate": enquiry_end.isoformat()
        }
        tender["tenderPeriod"] = {
            "startDate": tender["enquiryPeriod"]["endDate"],
            "endDate": calculate_tender_business_date(
                dt_from_iso(tender["enquiryPeriod"]["endDate"]),
                TENDERING_DURATION,
                tender,
            ).isoformat()
        }

    @staticmethod
    def watch_value_meta_changes(tender):
        pass  # TODO: shouldn't it work here

    @classmethod
    def find_agreement_unsuccessful_reason(cls, tender, agreement):
        if cls.is_agreement_not_active(agreement):
            return AGREEMENT_STATUS_MESSAGE

        if cls.are_tender_items_is_not_subset_of_agreement_items(tender, agreement):
            return AGREEMENT_ITEMS_MESSAGE

        if cls.is_agreement_expired(tender, agreement):
            return AGREEMENT_EXPIRED_MESSAGE.format(cls.agreement_min_period_until_end.days)

        elif cls.is_agreement_start_date_later(tender, agreement):
            return AGREEMENT_START_DATE_MESSAGE

        if cls.is_agreement_has_pending_changes(agreement):
            return AGREEMENT_CHANGE_MESSAGE

        if cls.has_insufficient_active_contracts(agreement):
            return AGREEMENT_CONTRACTS_MESSAGE.format(cls.agreement_min_active_contracts)

        if cls.has_mismatched_procuring_entities(tender, agreement):
            return AGREEMENT_IDENTIFIER_MESSAGE

    @classmethod
    def are_tender_items_is_not_subset_of_agreement_items(cls, tender, agreement):
        agreement_items_ids = {
            cls.calculate_item_identification_tuple(agreement_item)
            for agreement_item in agreement.get("items", "")
        }
        tender_items_ids = {
            cls.calculate_item_identification_tuple(tender_item)
            for tender_item in tender.get("items", "")
        }
        return not tender_items_ids.issubset(agreement_items_ids)

    @classmethod
    def is_agreement_expired(cls, tender, agreement):
        agreement_expire_date = calculate_tender_date(
            dt_from_iso(agreement["period"]["endDate"]),
            - cls.agreement_min_period_until_end,
            tender
        )
        return get_now() > agreement_expire_date

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
                raise_operation_error(
                    get_request(),
                    "Can't add features"
                )

    def validate_minimal_step(self, data, before=None):
        # override to skip minimalStep required validation
        # it's not required for cfaselectionua in tender level
        config = get_tender_config()
        kwargs = {
            "before": before,
            "enabled": config.get("hasAuction") is True,
        }
        validate_field(data, "minimalStep", required=False, **kwargs)

    def validate_tender_period_extension(self, tender):
        pass


class CFASelectionTenderDetailsState(CFASelectionTenderDetailsMixing, CFASelectionTenderState):
    pass


def calculate_agreement_contracts_value_amount(tender):
    agreement = tender["agreements"][0]
    tender_items = {i["id"]: i["quantity"]
                    for i in tender.get("items", "")}
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
        tender["value"] = tender["lots"][0]["value"] = value = max(
            contract_values,
            key=lambda value: value["amount"]
        )

        # handle minimalStep auto decrease
        minimal_step = tender["lots"][0].get("minimalStep")
        if minimal_step and minimal_step["amount"] > value["amount"]:
            tender["minimalStep"] = tender["lots"][0]["minimalStep"] = value


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
