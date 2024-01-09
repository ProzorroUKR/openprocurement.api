from openprocurement.tender.core.procedure.context import get_tender_config
from openprocurement.api.procedure.serializers.base import ListSerializer, BaseUIDSerializer
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.serializers.cancellation import CancellationSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from openprocurement.tender.core.procedure.serializers.award import AwardSerializer
from openprocurement.tender.core.procedure.serializers.lot import LotSerializer
from openprocurement.tender.core.procedure.serializers.qualification import QualificationSerializer


class TenderBaseSerializer(BaseUIDSerializer):
    base_private_fields = {
        "dialogue_token",
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "numberOfBids",
        "public_modified",
        "is_public",
        "is_test",
        "config",
    }
    serializers = {
        "bids": ListSerializer(BidSerializer),
        "qualifications": ListSerializer(QualificationSerializer),
        "cancellations": ListSerializer(CancellationSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "awards": ListSerializer(AwardSerializer),
        "lots": ListSerializer(LotSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        config = get_tender_config()

        self.private_fields = set(self.base_private_fields) | {"dialogue_token"}

        if config.get("hasPrequalification"):
            # if tender has pre-qualification bids are:
            # - fully private in: draft, active.enquiries, active.tendering
            # - partly private in: active.pre-qualification, active.pre-qualification.stand-still, active.auction
            # Rules for partly private bids are defined in the bid serializer
            private_bids_tender_statuses = (
                "draft",
                "active.enquiries",
                "active.tendering",
            )
        else:
            # if tender has no pre-qualification bids are:
            # - fully private in: draft, active.enquiries, active.tendering, active.auction
            private_bids_tender_statuses = (
                "draft",
                "active.enquiries",
                "active.tendering",
                "active.auction",
            )

        if data.get("status") in private_bids_tender_statuses:
            self.private_fields.add("bids")
