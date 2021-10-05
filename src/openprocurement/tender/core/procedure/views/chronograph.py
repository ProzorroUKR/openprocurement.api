from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.validation import validate_input_data
from openprocurement.tender.core.procedure.utils import save_tender, apply_data_patch
from openprocurement.tender.core.procedure.models.chronograph import TenderChronographData
from openprocurement.tender.core.procedure.serializers.chronograph import ChronographSerializer


class TenderChronographResource(TenderBaseResource):
    serializer_class = ChronographSerializer

    @json_view(permission="chronograph")
    def get(self):
        data = self.serializer_class(self.request.validated["tender"]).data
        return {"data": data}

    @json_view(
        permission="chronograph",
        validators=(
            validate_input_data(TenderChronographData),
        )
    )
    def patch(self):
        # 1 we run all event handlers that should be run by now
        self.state.run_time_events(self.request.validated["tender"])

        # 2 apply passed data ( auctionPeriod.startDate )
        data = self.request.validated["data"]
        updated = apply_data_patch(self.request.validated["tender"], data, none_means_remove=True)

        # 3 update tender state
        if updated:
            self.state.on_patch(self.request.validated["tender_src"], updated)
            self.request.validated["tender"] = updated
        else:
            self.state.always(self.request.validated["tender"])  # always updates next check and similar stuff

        # 4
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender by chronograph",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_chronograph_patch"})
            )
        return {"data": self.serializer_class(self.request.validated["tender"]).data}
