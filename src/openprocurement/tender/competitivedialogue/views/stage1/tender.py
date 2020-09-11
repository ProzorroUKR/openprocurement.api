# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource, save_tender
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_tender_change_status_with_cancellation_lot_pending,
    validate_tender_activate_with_criteria,
)
from openprocurement.api.utils import json_view, context_unpack, APIResource
from openprocurement.tender.belowthreshold.views.tender import TenderResource
from openprocurement.tender.openeu.views.tender import TenderEUResource
from openprocurement.tender.openua.validation import validate_patch_tender_ua_data
from openprocurement.tender.competitivedialogue.utils import patch_eu, set_ownership
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.validation import (
    validate_tender_update,
    validate_credentials_generation,
)


@optendersresource(
    name="{}:Tender".format(CD_EU_TYPE),
    path="/tenders/{tender_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Open Contracting compatible data exchange format. See  for more info",
)
class CompetitiveDialogueEUResource(TenderEUResource):
    """ Resource handler for Competitive Dialogue EU"""

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_ua_data,
            validate_tender_not_in_terminated_status,
            validate_tender_update,
            validate_tender_change_status_with_cancellation_lot_pending,
            validate_tender_activate_with_criteria,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return patch_eu(self)


@optendersresource(
    name="{}:Tender".format(CD_UA_TYPE),
    path="/tenders/{tender_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Open Contracting compatible data exchange format. See # for more info",
)
class CompetitiveDialogueUAResource(TenderResource):
    """ Resource handler for Competitive Dialogue UA"""

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_tender_ua_data,
            validate_tender_not_in_terminated_status,
            validate_tender_update,
            validate_tender_change_status_with_cancellation_lot_pending,
            validate_tender_activate_with_criteria,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return patch_eu(self)


@optendersresource(
    name="{}:Tender credentials".format(STAGE_2_EU_TYPE),
    path="/tenders/{tender_id}/credentials",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender stage2 UE credentials",
)
class TenderStage2EUCredentialsResource(APIResource):
    @json_view(permission="generate_credentials", validators=(validate_credentials_generation))
    def patch(self):
        tender = self.request.validated["tender"]

        access = set_ownership(tender)
        if save_tender(self.request):
            self.LOGGER.info(
                "Generate Tender stage2 credentials {}".format(tender.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"}),
            )
            return {"data": tender.serialize("view"), "access": access}


@optendersresource(
    name="{}:Tender credentials".format(STAGE_2_UA_TYPE),
    path="/tenders/{tender_id}/credentials",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender stage2 UA credentials",
)
class TenderStage2UACredentialsResource(TenderStage2EUCredentialsResource):
    pass
