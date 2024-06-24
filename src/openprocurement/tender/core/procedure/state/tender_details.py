from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from openprocurement.api.constants import (
    CPV_PREFIX_LENGTH_TO_NAME,
    MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM,
    MILESTONES_VALIDATION_FROM,
    RELATED_LOT_REQUIRED_FROM,
    RELEASE_ECRITERIA_ARTICLE_17,
    TENDER_CONFIG_JSONSCHEMAS,
    TENDER_CONFIG_OPTIONALITY,
    TENDER_PERIOD_START_DATE_STALE_MINUTES,
)
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_agreement, get_object, get_tender
from openprocurement.api.procedure.utils import (
    get_cpv_prefix_length,
    get_cpv_uniq_prefixes,
    to_decimal,
)
from openprocurement.api.utils import get_first_revision_date, raise_operation_error
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.constants import (
    AGREEMENT_CONTRACTS_MESSAGE,
    AGREEMENT_IDENTIFIER_MESSAGE,
    AGREEMENT_NOT_FOUND_MESSAGE,
    AGREEMENT_STATUS_MESSAGE,
    LIMITED_PROCUREMENT_METHOD_TYPES,
    PROCUREMENT_METHOD_LIMITED,
    PROCUREMENT_METHOD_OPEN,
    PROCUREMENT_METHOD_SELECTIVE,
    SELECTIVE_PROCUREMENT_METHOD_TYPES,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    set_mode_test_titles,
    tender_created_after,
    tender_created_before,
    validate_field,
)
from openprocurement.tender.core.utils import (
    calculate_complaint_business_date,
    calculate_tender_business_date,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    COMPETITIVE_ORDERING,
)
from openprocurement.tender.pricequotation.constants import PQ


class TenderConfigMixin:
    configurations = (
        "hasAuction",
        "hasAwardingOrder",
        "hasValueRestriction",
        "valueCurrencyEquality",
        "hasPrequalification",
        "minBidsNumber",
        "hasPreSelectionAgreement",
        "hasTenderComplaints",
        "hasAwardComplaints",
        "hasCancellationComplaints",
        "restricted",
    )

    def validate_config(self, data):
        for config_name in self.configurations:
            value = data["config"].get(config_name)

            if value is None and TENDER_CONFIG_OPTIONALITY.get(config_name, True) is False:
                raise_operation_error(
                    self.request,
                    "This field is required.",
                    status=422,
                    location="body",
                    name=config_name,
                )

            procurement_method_type = data.get("procurementMethodType")
            config_schema = TENDER_CONFIG_JSONSCHEMAS.get(procurement_method_type)
            if not config_schema:
                raise NotImplementedError
            schema = config_schema["properties"][config_name]
            try:
                validate(value, schema)
            except ValidationError as e:
                raise_operation_error(
                    self.request,
                    e.message,
                    status=422,
                    location="body",
                    name=config_name,
                )

        self.validate_restricted_config(data)

    def validate_restricted_config(self, data):
        has_restricted_preselection_agreement = False
        agreement = get_agreement()
        if agreement:
            has_restricted_preselection_agreement = agreement["config"]["restricted"] is True
        if has_restricted_preselection_agreement is True and data["config"]["restricted"] is False:
            raise_operation_error(
                self.request,
                "Value must be True.",
                status=422,
                location="body",
                name="restricted",
            )
        elif has_restricted_preselection_agreement is False and data["config"]["restricted"] is True:
            raise_operation_error(
                self.request,
                "Value must be False.",
                status=422,
                location="body",
                name="restricted",
            )


class TenderDetailsMixing(TenderConfigMixin):
    """
    describes business logic rules for tender owners
    when they prepare tender for tendering stage
    """

    config: dict

    tender_create_accreditations = None
    tender_central_accreditations = None
    tender_edit_accreditations = None

    required_criteria = ()

    enquiry_period_timedelta: timedelta
    enquiry_stand_still_timedelta: timedelta
    pre_qualification_complaint_stand_still = timedelta(days=0)
    tendering_period_extra_working_days = False
    agreement_min_active_contracts = 3
    should_validate_cpv_prefix = True
    should_validate_pre_selection_agreement = True
    complaint_submit_time = timedelta(days=0)
    agreement_field = "agreements"

    def validate_tender_patch(self, before, after):
        request = get_request()
        if before["status"] != after["status"]:
            self.validate_cancellation_blocks(request, before)

    def on_post(self, tender):
        self.validate_config(tender)
        self.validate_procurement_method(tender)
        self.validate_lots_count(tender)
        self.validate_milestones(tender)
        self.validate_minimal_step(tender)
        self.validate_submission_method(tender)
        self.validate_items_classification_prefix(tender)
        self.watch_value_meta_changes(tender)
        self.update_complaint_period(tender)
        self.update_date(tender)
        super().on_post(tender)

        # set author for documents passed with tender data
        for doc in tender.get("documents", ""):
            doc["author"] = "tender_owner"

    def on_patch(self, before, after):
        self.validate_procurement_method(after, before=before)
        self.validate_lots_count(after)
        self.validate_milestones(after)
        self.validate_pre_qualification_status_change(before, after)
        self.validate_tender_period_start_date_change(before, after)
        self.validate_minimal_step(after, before=before)
        self.validate_submission_method(after, before=before)
        self.validate_kind_change(after, before)
        self.validate_award_criteria_change(after, before)
        self.validate_items_classification_prefix(after)
        self.validate_action_with_exist_inspector_review_request(("tenderPeriod",))
        self.update_complaint_period(after)
        self.watch_value_meta_changes(after)
        self.validate_required_criteria(before, after)
        self.invalidate_review_requests()
        self.validate_remove_inspector(before, after)
        super().on_patch(before, after)

    def always(self, data):
        self.set_mode_test(data)
        super().always(data)

    def status_up(self, before, after, data):
        if after == "draft" and before != "draft":
            raise_operation_error(
                get_request(), "Can't change status to draft", status=422, location="body", name="status"
            )
        if after != "draft" and before == "draft":
            self.validate_pre_selection_agreement(data)
        elif after == "active.tendering" and before != "active.tendering":
            tendering_start = data["tenderPeriod"]["startDate"]
            if dt_from_iso(tendering_start) <= get_now() - timedelta(minutes=TENDER_PERIOD_START_DATE_STALE_MINUTES):
                raise_operation_error(
                    get_request(),
                    "tenderPeriod.startDate should be in greater than current date",
                    status=422,
                    location="body",
                    name="tenderPeriod.startDate",
                )
        super().status_up(before, after, data)

    def validate_pre_selection_agreement(self, tender):
        if self.should_validate_pre_selection_agreement is False:
            return

        def raise_agreements_error(message):
            raise_operation_error(
                self.request,
                message,
                status=422,
                location="body",
                name=self.agreement_field,
            )

        if tender["config"]["hasPreSelectionAgreement"] is True:
            agreements = [tender["agreement"]] if tender.get("agreement") else tender.get("agreements")
            if not agreements:
                raise_agreements_error("This field is required.")

            if len(agreements) != 1:
                raise_agreements_error("Exactly one agreement is expected.")

            agreement = get_object("agreement")

            if not agreement:
                raise_agreements_error(AGREEMENT_NOT_FOUND_MESSAGE)

            tender_agreement_type_mapping = {
                COMPETITIVE_ORDERING: DPS_TYPE,
                PQ: ELECTRONIC_CATALOGUE_TYPE,
            }

            if tender_agreement_type_mapping[tender["procurementMethodType"]] != agreement["agreementType"]:
                raise_agreements_error("Agreement type mismatch.")

            if self.is_agreement_not_active(agreement):
                raise_agreements_error(AGREEMENT_STATUS_MESSAGE)

            if self.has_insufficient_active_contracts(agreement):
                raise_agreements_error(AGREEMENT_CONTRACTS_MESSAGE.format(self.agreement_min_active_contracts))

            if self.has_mismatched_procuring_entities(tender, agreement):
                raise_agreements_error(AGREEMENT_IDENTIFIER_MESSAGE)

    def set_mode_test(self, tender):
        if tender["config"].get("test"):
            tender["mode"] = "test"
        if tender.get("mode") == "test":
            set_mode_test_titles(tender)

    def validate_milestones(self, tender):
        grouped_data = defaultdict(list)
        sums = {
            "financing": defaultdict(Decimal),
            "delivery": defaultdict(Decimal),
        }
        related_lot_exists = False
        for milestone in tender.get("milestones", []):
            if milestone.get("type") == "financing":
                if (
                    get_first_revision_date(tender, default=get_now()) > MILESTONES_VALIDATION_FROM
                    and milestone.get("duration", {}).get("days", 0) > 1000
                ):
                    raise_operation_error(
                        get_request(),
                        [{"duration": ["days shouldn't be more than 1000 for financing milestone"]}],
                        status=422,
                        name="milestones",
                    )
            sums[milestone["type"]][milestone.get("relatedLot")] += to_decimal(milestone.get("percentage", 0))
            grouped_data[milestone.get('relatedLot')].append(milestone)

            if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM) and milestone.get('relatedLot'):
                related_lot_exists = True

        if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM):
            for lot, milestones in grouped_data.items():
                for i, milestone in enumerate(milestones):
                    if related_lot_exists and not milestone.get('relatedLot'):
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
                    if milestone.get("sequenceNumber") != i + 1:
                        raise_operation_error(
                            get_request(),
                            [
                                {
                                    "sequenceNumber": "Field should contain incrementing sequence numbers starting from 1 for tender/lot separately"
                                }
                            ],
                            status=422,
                            name="milestones",
                        )
        for milestone_type, values in sums.items():
            for uid, sum_value in values.items():
                if sum_value != Decimal("100"):
                    raise_operation_error(
                        get_request(),
                        f"Sum of the {milestone_type} milestone percentages {sum_value} "
                        f"is not equal 100{f' for lot {uid}' if uid else ''}.",
                        status=422,
                        name="milestones",
                    )

    def validate_lots_count(self, tender):
        tender = get_tender()
        if tender.get("procurementMethodType") == COMPETITIVE_ORDERING:
            # TODO: consider using config
            max_lots_count = 1
            if len(tender.get("lots", "")) > max_lots_count:
                raise_operation_error(
                    get_request(),
                    "Can't create more than {} lots".format(max_lots_count),
                    status=422,
                    location="body",
                    name="lots",
                )

    def validate_pre_qualification_status_change(self, before, after):
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
                    i["status"] in self.block_complaint_status
                    for q in after["qualifications"]
                    for i in q.get("complaints", "")
                    if q.get("lotID") in active_lots
                ):
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.pre-qualification.stand-still' before resolve all complaints",
                    )

                if self.all_bids_are_reviewed(after):
                    after["qualificationPeriod"]["endDate"] = calculate_complaint_business_date(
                        get_now(), self.pre_qualification_complaint_stand_still, after
                    ).isoformat()
                    after["qualificationPeriod"]["reportingDatePublication"] = get_now().isoformat()
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
        now = get_now().isoformat()
        tender["date"] = now

        for lot in tender.get("lots", ""):
            lot["date"] = now

    @staticmethod
    def watch_value_meta_changes(tender):
        # tender currency and valueAddedTaxIncluded must be specified only ONCE
        # instead it's specified in many places but we need keep them the same
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

    @classmethod
    def validate_required_criteria(cls, before, after):
        if tender_created_before(RELEASE_ECRITERIA_ARTICLE_17):
            return

        if after.get("status") not in ("active", "active.tendering"):
            return

        tender_criteria = {
            criterion["classification"]["id"]
            for criterion in after.get("criteria", "")
            if criterion.get("classification")
        }

        # exclusion criteria
        if set(cls.required_criteria) - tender_criteria:
            raise_operation_error(
                get_request(),
                f"Tender must contain all required criteria: {', '.join(sorted(cls.required_criteria))}",
            )

    def validate_minimal_step(self, data, before=None):
        """
        Minimal step validation.
        Minimal step should be required if tender has auction

        :param data: tender or lot
        :param before: tender or lot
        :return:
        """
        tender = get_tender()
        kwargs = {
            "before": before,
            "enabled": tender["config"]["hasAuction"] is True,
        }
        validate_field(data, "minimalStep", **kwargs)

    def validate_submission_method(self, data, before=None):
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

    def validate_items_classification_prefix(self, tender):
        if not self.should_validate_cpv_prefix:
            return

        # tender.items.classification
        classifications = [item["classification"] for item in tender.get("items", "")]

        prefix_length = get_cpv_prefix_length(classifications)
        prefix_name = CPV_PREFIX_LENGTH_TO_NAME[prefix_length]
        if len(get_cpv_uniq_prefixes(classifications, prefix_length)) != 1:
            raise_operation_error(
                get_request(), [f"CPV {prefix_name} of items should be identical"], status=422, name="items"
            )

        if not self.should_validate_pre_selection_agreement:
            return

        agreements = tender.get("agreements")

        if not agreements:
            return

        agreement = get_object("agreement")

        if not agreement:
            return

        # tender.items.classification + agreement.classification
        classifications.append(agreement["classification"])

        prefix_length = get_cpv_prefix_length(classifications)
        prefix_name = CPV_PREFIX_LENGTH_TO_NAME[prefix_length]
        if len(get_cpv_uniq_prefixes(classifications, prefix_length)) != 1:
            raise_operation_error(
                get_request(),
                [f"CPV {prefix_name} of items should be identical to agreement cpv"],
                status=422,
                name="items",
            )

    @classmethod
    def validate_items_classification_prefix_unchanged(cls, before, after):
        prefix_list = set()
        prefix_length = 3  # group
        for item in before.get("items", ""):
            prefix_list.add(item["classification"]["id"][:prefix_length])
        for item in after.get("items", ""):
            prefix_list.add(item["classification"]["id"][:prefix_length])
        if len(prefix_list) != 1:
            prefix_name = CPV_PREFIX_LENGTH_TO_NAME[prefix_length]
            raise_operation_error(
                get_request(), [f"Can't change classification {prefix_name} of items"], status=422, name="items"
            )

    def validate_tender_period_extension(self, tender):
        if "tenderPeriod" in tender and "endDate" in tender["tenderPeriod"]:
            tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
            if (
                calculate_tender_business_date(
                    get_now(),
                    self.tendering_period_extra,
                    tender=tender,
                    working_days=self.tendering_period_extra_working_days,
                )
                > tendering_end
            ):
                raise_operation_error(
                    get_request(),
                    "tenderPeriod should be extended by {0.days} {1}".format(
                        self.tendering_period_extra,
                        "working days" if self.tendering_period_extra_working_days else "days",
                    ),
                )

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

    @classmethod
    def has_insufficient_active_contracts(cls, agreement):
        active_contracts_count = sum(c["status"] == "active" for c in agreement.get("contracts", ""))
        return active_contracts_count < cls.agreement_min_active_contracts

    @classmethod
    def has_mismatched_procuring_entities(cls, tender, agreement):
        agreement_identifier = agreement["procuringEntity"]["identifier"]
        tender_identifier = tender["procuringEntity"]["identifier"]
        return (
            tender_identifier["id"] != agreement_identifier["id"]
            or tender_identifier["scheme"] != agreement_identifier["scheme"]
        )

    def validate_related_lot_in_items(self, after):
        if (
            tender_created_after(RELATED_LOT_REQUIRED_FROM)
            or after.get("procurementMethodType") in ABOVE_THRESHOLD_GROUP
        ) and after["status"] != "draft":
            for item in after["items"]:
                if not item.get("relatedLot"):
                    raise_operation_error(
                        get_request(), "This field is required", status=422, location="body", name="item.relatedLot"
                    )

    def update_complaint_period(self, tender):
        if tender["config"]["hasTenderComplaints"] is not True:
            return
        if "tenderPeriod" not in tender or "endDate" not in tender["tenderPeriod"]:
            return
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_complaint_business_date(tendering_end, -self.complaint_submit_time, tender)
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


class TenderDetailsState(TenderDetailsMixing, TenderState):
    pass
