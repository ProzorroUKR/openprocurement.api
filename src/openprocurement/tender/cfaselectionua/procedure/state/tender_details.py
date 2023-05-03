from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_date
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState
from openprocurement.tender.cfaselectionua.constants import (
    AGREEMENT_NOT_FOUND,
    AGREEMENT_STATUS,
    AGREEMENT_ITEMS,
    AGREEMENT_EXPIRED,
    AGREEMENT_CHANGE,
    AGREEMENT_CONTRACTS,
    AGREEMENT_IDENTIFIER,
    AGREEMENT_START_DATE,
    MIN_PERIOD_UNTIL_AGREEMENT_END,
    MIN_ACTIVE_CONTRACTS,
    ENQUIRY_PERIOD,
    TENDERING_DURATION,
    MINIMAL_STEP_PERCENTAGE,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.api.utils import raise_operation_error
from copy import deepcopy


class CFASelectionTenderDetailsMixing(TenderDetailsMixing):

    def on_post(self, tender):
        super().on_post(tender)
        self.check_owner_forbidden_fields(tender)

    def on_patch(self, before, after):
        if get_request().authenticated_role == "agreement_selection":
            if after["status"] == "active.enquiries":
                reason = self.find_unsuccessful_reason(after)
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
                after["unsuccessfulReason"] = [AGREEMENT_NOT_FOUND]
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

    @staticmethod
    def find_unsuccessful_reason(tender):
        agreement = tender["agreements"][0]
        if agreement.get("status") != "active":
            return AGREEMENT_STATUS

        # ---
        agreement_items_ids = {calculate_item_identification_tuple(agreement_item)
                               for agreement_item in agreement.get("items", "")}
        tender_items_ids = {calculate_item_identification_tuple(tender_item)
                            for tender_item in tender.get("items", "items")}
        if not tender_items_ids.issubset(agreement_items_ids):
            return AGREEMENT_ITEMS

        agreement_expire_date = calculate_tender_date(
            dt_from_iso(agreement["period"]["endDate"]),
            - MIN_PERIOD_UNTIL_AGREEMENT_END,
            tender
        )

        if get_now() > agreement_expire_date:
            return AGREEMENT_EXPIRED

        elif agreement["period"]["startDate"] > tender["date"]:
            return AGREEMENT_START_DATE

        # ---
        for change in agreement.get("changes", ""):
            if change["status"] == "pending":
                return AGREEMENT_CHANGE

        # --
        for agr in tender["agreements"]:
            active_contracts_count = sum(
                c["status"] == "active" for c in agr.get("contracts", "")
            )

            if active_contracts_count < MIN_ACTIVE_CONTRACTS:
                return AGREEMENT_CONTRACTS

        # --
        if agreement.get("procuringEntity"):
            agreement_identifier = agreement["procuringEntity"]["identifier"]
            tender_identifier = tender["procuringEntity"]["identifier"]
            if (
                tender_identifier["id"] != agreement_identifier["id"]
                or tender_identifier["scheme"] != agreement_identifier["scheme"]
            ):
                return AGREEMENT_IDENTIFIER

    @staticmethod
    def check_owner_forbidden_fields(tender):
        if tender["status"] in ("draft", "draft.pending"):
            if "features" in tender:
                raise_operation_error(
                    get_request(),
                    "Can't add features"
                )


class TenderDetailsState(CFASelectionTenderDetailsMixing, CFASelectionTenderState):
    pass


def calculate_item_identification_tuple(item):
    result = (
        item["id"],
        item["classification"]["id"],
        item["classification"]["scheme"],
        item["unit"]["code"] if item.get("unit") else None,
        tuple((c["id"], c["scheme"]) for c in item.get("additionalClassifications", ""))
    )
    return result


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
