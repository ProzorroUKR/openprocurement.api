from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.constants import CHRONOGRAPH_PATCH_LOG_FIELDS
from openprocurement.tender.core.procedure.models.chronograph import (
    TenderChronographData,
)
from openprocurement.tender.core.procedure.serializers.chronograph import (
    ChronographSerializer,
)
from openprocurement.tender.core.procedure.utils import (
    filter_nested_values,
    save_tender,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


class TenderChronographResource(TenderBaseResource):
    serializer_class = ChronographSerializer

    @json_view(permission="chronograph")
    def get(self):
        tender = get_tender()
        return {
            "data": self.serializer_class(tender).data,
            "config": tender["config"],
        }

    @json_view(
        permission="chronograph",
        validators=(validate_input_data(TenderChronographData),),
    )
    def patch(self):
        # 1 we convert [{"auctionPeriod": {"startDate": "2020.."}}, {"auctionPeriod": None}]
        #           to [{"auctionPeriod": {"startDate": "2020.."}}, {}]
        # TODO find a better way to specify partial update

        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        tender_src = self.request.validated["tender_src"]

        for lot in data.get("lots", ""):
            if "auctionPeriod" in lot and lot["auctionPeriod"] is None:
                del lot["auctionPeriod"]

        # 2 apply passed data ( auctionPeriod.startDate )
        updated = apply_data_patch(tender, data)
        if updated:
            tender = self.request.validated["tender"] = updated

        # 3 we run all event handlers that should be run by now
        self.state.run_time_events(tender)

        # 4 update tender state
        if updated:
            self.state.on_patch(tender_src, tender)
        else:
            self.state.always(tender)  # always updates next check and similar stuff

        # 5 save
        saved = save_tender(self.request)

        # prepare log context
        LOG_CONTEXT = {
            "before": filter_nested_values(tender_src, *CHRONOGRAPH_PATCH_LOG_FIELDS),
            "after": filter_nested_values(tender, *CHRONOGRAPH_PATCH_LOG_FIELDS),
        }

        # log result
        if saved:
            self.LOGGER.info(
                "Updated tender by chronograph",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_chronograph_patch"},
                    {"CONTEXT": LOG_CONTEXT},
                ),
            )
        else:
            self.LOGGER.warning(
                "No changes to tender by chronograph",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_chronograph_patch_no_changes"},
                    {"CONTEXT": LOG_CONTEXT},
                ),
            )

        # return result
        return {
            "data": self.serializer_class(tender).data,
            "config": tender["config"],
        }
