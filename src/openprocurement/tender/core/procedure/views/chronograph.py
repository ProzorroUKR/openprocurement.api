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
        tender = self.request.validated["tender"]
        tender_config = self.request.validated["tender_config"]
        return {
            "data": self.serializer_class(tender).data,
            "config": self.serializer_config_class(tender_config).data,
        }

    @json_view(
        permission="chronograph",
        validators=(
            validate_input_data(TenderChronographData),
        )
    )
    def patch(self):
        tender_config = self.request.validated["tender_config"]

        # 1 we convert [{"auctionPeriod": {"startDate": "2020.."}}, {"auctionPeriod": None}]
        #           to [{"auctionPeriod": {"startDate": "2020.."}}, {}]
        # TODO find a better way to specify partial update
        data = self.request.validated["data"]
        for lot in data.get("lots", ""):
            if "auctionPeriod" in lot and lot["auctionPeriod"] is None:
                del lot["auctionPeriod"]

        # 2 apply passed data ( auctionPeriod.startDate )
        updated = apply_data_patch(self.request.validated["tender"], data)
        if updated:
            self.request.validated["tender"] = updated

        # 3 we run all event handlers that should be run by now
        self.state.run_time_events(self.request.validated["tender"])

        # 4 update tender state
        if updated:
            self.state.on_patch(self.request.validated["tender_src"], updated)
        else:
            self.state.always(self.request.validated["tender"])  # always updates next check and similar stuff

        # 5 save
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender by chronograph",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_chronograph_patch"})
            )
        return {
            "data": self.serializer_class(self.request.validated["tender"]).data,
            "config": self.serializer_config_class(tender_config).data,
        }
