from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules


class CancellationBlockMixing:
    @staticmethod
    def cancellation_blocks_tender(tender, lot_id=None):
        """
        A pending cancellation stop the tender process
        until the either tender is cancelled or cancellation is cancelled 🤯
        :param tender:
        :param lot_id: if passed, then other lot cancellations are not considered
        :return:
        """
        if not tender_created_after_2020_rules():
            return False

        if tender["procurementMethodType"] in (
            "belowThreshold",
            "closeFrameworkAgreementSelectionUA",
            "requestForProposal",
        ):
            return False

        related_cancellations = [
            c
            for c in tender.get("cancellations", "")
            if lot_id is None  # we don't care of lot
            or c.get("relatedLot") in (None, lot_id)  # it's tender or this lot cancellation
        ]

        if any(i["status"] == "pending" for i in related_cancellations):
            return True

        # unsuccessful also blocks tender
        accept_tender = all(
            any(complaint["status"] == "resolved" for complaint in c.get("complaints"))
            for c in related_cancellations
            if c["status"] == "unsuccessful" and c.get("complaints")
        )
        return not accept_tender

    def validate_cancellation_blocks(self, request, tender, lot_id=None):
        if self.cancellation_blocks_tender(tender, lot_id):
            raise_operation_error(request, "Can't perform action due to a pending cancellation")
