from cornice.resource import resource

from openprocurement.api.utils import json_view, raise_operation_error
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.utils import (
    context_unpack,
    save_tender,
    set_ownership,
)
from openprocurement.tender.core.procedure.validation import validate_dialogue_owner
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


@resource(
    name="{}:Tender credentials".format(STAGE_2_EU_TYPE),
    path="/tenders/{tender_id}/credentials",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender stage2 UE credentials",
)
class CD2EUCredentialsResource(TenderBaseResource):
    serializer_class = TenderBaseSerializer

    @json_view(
        permission="edit_tender",
        validators=(validate_dialogue_owner,),
    )
    def patch(self):
        tender = self.request.validated["tender"]
        if tender["status"] != "draft.stage2":
            raise_operation_error(
                self.request, f"Can't generate credentials in current ({tender['status']}) contract status"
            )

        access = set_ownership(tender, self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                f"Generate Tender stage2 credentials {tender['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"}),
            )
            return {"data": self.serializer_class(tender).data, "access": access}


@resource(
    name="{}:Tender credentials".format(STAGE_2_UA_TYPE),
    path="/tenders/{tender_id}/credentials",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender stage2 UA credentials",
)
class CD2UACredentialsResource(CD2EUCredentialsResource):
    pass
