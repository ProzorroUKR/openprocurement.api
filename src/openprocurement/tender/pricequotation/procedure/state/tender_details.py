from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5
from openprocurement.api.constants import CONTRACT_TEMPLATES_KEYS
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_object
from openprocurement.api.utils import get_tender_profile, raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.pricequotation.constants import DEFAULT_TEMPLATE_KEY
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class TenderDetailsState(TenderDetailsMixing, PriceQuotationTenderState):
    tender_create_accreditations = (ACCR_1, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_2,)

    required_criteria = ()

    should_validate_pre_selection_agreement = True
    should_validate_cpv_prefix = False
    agreement_field = "agreement"

    def on_post(self, tender):
        self.validate_agreement_exists()
        super().on_post(tender)

    def validate_agreement_exists(self):
        agreement = get_object("agreement")
        if not agreement:
            raise_operation_error(
                self.request,
                {"id": ["id must be one of exists agreement"]},
                status=422,
                name=self.agreement_field,
            )

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

        if before == "draft" and after == "active.tendering":
            if not data.get("noticePublicationDate"):
                data["noticePublicationDate"] = get_now().isoformat()
            data["tenderPeriod"]["startDate"] = get_now().isoformat()

        # TODO: it's insurance for some period while refusing PQ bot, just to have opportunity manually activate tender
        if before == "draft.publishing" and after == "active.tendering":
            self.validate_pre_selection_agreement(data)
            data["tenderPeriod"]["startDate"] = get_now().isoformat()

        if before == "draft.unsuccessful" and after != before:
            raise_operation_error(
                get_request(),
                f"Can't change status from {before} to {after}",
            )

        if after == "active.tendering" and after != before:
            self.set_contract_template_name(data)

        if after in self.unsuccessful_statuses:
            self.set_contracts_cancelled(after)

    def set_contract_template_name(self, data):
        EXCLUDED_TEMPLATE_CLASSIFICATION = ("0931",)

        items = data.get("items")
        if not items or any(i.get("documentType", "") == "contractProforma" for i in data.get("documents", "")):
            return

        classification_id = items[0].get("classification", dict()).get("id")
        template_name = None
        if not classification_id:
            return

        classification_id = classification_id[:4] if classification_id[:3] != "336" else "336"
        if classification_id not in EXCLUDED_TEMPLATE_CLASSIFICATION:
            for key in CONTRACT_TEMPLATES_KEYS:
                if key.startswith(classification_id):
                    template_name = key
                    break
                elif key.startswith(DEFAULT_TEMPLATE_KEY):
                    template_name = key

        if template_name:
            data["contractTemplateName"] = template_name

    def has_mismatched_procuring_entities(self, tender, agreement):
        pass

    def has_insufficient_active_contracts(self, agreement):
        pass

    def validate_pre_selection_agreement(self, tender):
        self.validate_profiles(tender)
        super().validate_pre_selection_agreement(tender)

    def validate_profiles(self, tender):
        profile_ids = []
        if "profile" in tender:
            profile_ids = [tender["profile"]]
        else:
            for items in tender.get("items", []):
                profile_id = items.get("profile")
                if profile_id:
                    profile_ids.append(profile_id)
        if not profile_ids:
            raise_operation_error(
                self.request,
                f"Profiles not found in tender {tender['_id']}",
                status=422,
            )

        for profile_id in profile_ids:
            profile = get_tender_profile(self.request, profile_id)
            profile_status = profile.get("status")
            if profile_status not in ("active", "general"):
                raise_operation_error(
                    self.request,
                    f"Profile {profile_id} is not active",
                    status=422,
                )

            profile_agreement_id = profile.get("agreementID")
            tender_agreement_id = tender.get("agreement", {}).get("id")
            if profile_agreement_id != tender_agreement_id:
                raise_operation_error(
                    self.request,
                    "Tender agreement doesn't match profile agreement",
                    status=422,
                )
