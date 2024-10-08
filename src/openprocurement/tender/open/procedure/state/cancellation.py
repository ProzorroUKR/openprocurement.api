from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenUACancellationStateMixing(CancellationStateMixing):
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
        "noOffer",
    ]

    def validate_cancellation_post(self, data):
        super().validate_cancellation_post(data)
        request, tender = get_request(), get_tender()
        self.validate_not_only_unsuccessful_awards_or_qualifications(request, tender, data)

    def validate_cancellation_patch(self, before, after):
        super().validate_cancellation_patch(before, after)
        request, tender = get_request(), get_tender()
        self.validate_not_only_unsuccessful_awards_or_qualifications(request, tender, before)

    @staticmethod
    def validate_not_only_unsuccessful_awards_or_qualifications(request, tender, cancellation):
        items = tender.get("awards") or tender.get("qualifications", "")

        def check_lot_items(uid, unsuccessful_statuses=("unsuccessful", "cancelled")):
            statuses = {i["status"] for i in items if i.get("lotID") == uid}
            if statuses and not statuses.difference(unsuccessful_statuses):
                raise_operation_error(
                    request,
                    "Can't perform cancellation if all {} are unsuccessful".format(
                        "awards" if tender.get("awards") else "qualifications"
                    ),
                )

        lot_id = cancellation.get("relatedLot")
        lots = tender.get("lots", "")
        if lots and not lot_id:
            # cancelling tender with lots
            # can't cancel tender if there is a lot, where
            for lot in lots:
                if lot["status"] == "active":
                    check_lot_items(lot["id"])

        elif lots and lot_id or not lot_id and not lots:
            # cancelling lot or tender without lots
            check_lot_items(lot_id)


class OpenCancellationState(OpenUACancellationStateMixing, OpenTenderState):
    pass
