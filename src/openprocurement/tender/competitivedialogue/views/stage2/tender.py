# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource, save_tender
from openprocurement.api.views.base import BaseResource
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.competitivedialogue.utils import set_ownership
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.validation import (
    validate_credentials_generation,
)


@optendersresource(
    name="{}:Tender credentials".format(STAGE_2_EU_TYPE),
    path="/tenders/{tender_id}/credentials",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender stage2 UE credentials",
)
class TenderStage2EUCredentialsResource(BaseResource):
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
