from datetime import timedelta

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.cfaua.constants import CFA_UA_TENDERING_EXTRA_PERIOD
from openprocurement.tender.cfaua.procedure.models.tender import CFAPatchTender, CFAPostTender, CFATender
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.core.utils import calculate_tender_full_date


class CFAUATenderDetailsMixin(TenderDetailsMixin):
    post_data_model = CFAPostTender
    patch_data_model = CFAPatchTender
    data_model = CFATender

    tender_patch_allowed_statuses = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.qualification",
    )
    required_multilingual_fields = {
        "procuringEntity": {
            "contactPoint": {"name_en": True},
            "additionalContactPoints": {"name_en": True},
        },
        "items": {"description_en": True},
    }
    procuring_entity_available_language_default = "uk"
    main_procurement_category_choices = ("goods", "services")
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.qualification",
        "active.qualification.stand-still",
    )
    tender_period_extra = CFA_UA_TENDERING_EXTRA_PERIOD
    notice_doc_required_check = False
    required_market_criteria_check = False
    status_up_allowed_transitions = (
        ("draft", "active.tendering"),
        ("active.pre-qualification", "active.pre-qualification.stand-still"),
        ("active.pre-qualification.stand-still", "active.pre-qualification"),
        ("active.qualification", "active.qualification.stand-still"),
    )
    watch_value_meta_changes_enabled = False
    all_documents_should_be_public = True

    def on_patch(self, before, after):
        self.validate_qualification_status_change(before, after)
        super().on_patch(before, after)  # TenderDetailsMixin.on_patch

    def validate_qualification_status_change(self, before, after):
        tender = get_tender()
        award_complain_duration = tender["config"]["awardComplainDuration"]
        if before["status"] == "active.qualification":
            passed_data = get_request().validated["json_data"]
            if passed_data != {"status": "active.qualification.stand-still"}:
                raise_operation_error(
                    get_request(),
                    "Can't update tender at 'active.qualification' status",
                )
            else:  # switching to active.qualification.stand-still
                lots = after.get("lots")
                if lots:
                    active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
                else:
                    active_lots = {None}

                if any(
                    self.is_blocking_complaint(i)
                    for q in after["awards"]
                    for i in q.get("complaints", "")
                    if q.get("lotID") in active_lots
                ):
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.qualification.stand-still' before resolve all complaints",
                    )

                if self.all_awards_are_reviewed(after):
                    after["awardPeriod"]["endDate"] = calculate_tender_full_date(
                        get_request_now(),
                        timedelta(days=award_complain_duration),
                        tender=after,
                        working_days=False,
                        calendar=self.calendar,
                    ).isoformat()
                    for award in after["awards"]:
                        if award["status"] != "cancelled" and award_complain_duration > 0:
                            award["complaintPeriod"] = {
                                "startDate": get_request_now().isoformat(),
                                "endDate": after["awardPeriod"]["endDate"],
                            }
                else:
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.qualification.stand-still' while not all awards are qualified",
                    )

        # before status != active.qualification
        elif after["status"] == "active.qualification.stand-still":
            raise_operation_error(
                get_request(),
                f"Can't switch to 'active.qualification.stand-still' from {before['status']}",
            )


class CFAUATenderDetailsState(CFAUATenderDetailsMixin, CFAUATenderState):
    pass
