from openprocurement.tender.cfaua.procedure.serializers.bid import BidSerializer
from openprocurement.tender.cfaua.procedure.serializers.agreement import AgreementSerializer
from openprocurement.tender.cfaua.procedure.serializers.guarantee import GuaranteeSerializer
from openprocurement.tender.core.procedure.serializers.lot import LotSerializer
from openprocurement.tender.core.procedure.serializers.qualification import QualificationSerializer
from openprocurement.tender.core.procedure.serializers.base import ListSerializer
from openprocurement.tender.core.procedure.serializers.tender import TenderBaseSerializer
from openprocurement.tender.core.procedure.serializers.cancellation import CancellationSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from openprocurement.tender.core.procedure.serializers.award import AwardSerializer
from openprocurement.tender.core.procedure.serializers.feature import FeatureSerializer


class CFAUATenderSerializer(TenderBaseSerializer):
    serializers = {
        "bids": ListSerializer(BidSerializer),
        "qualifications": ListSerializer(QualificationSerializer),
        "cancellations": ListSerializer(CancellationSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "awards": ListSerializer(AwardSerializer),
        "lots": ListSerializer(LotSerializer),
        "features": ListSerializer(FeatureSerializer),
        "agreements": ListSerializer(AgreementSerializer),
        "guarantee": GuaranteeSerializer,
    }

    def __init__(self, data: dict):
        super().__init__(data)

        self.private_fields = set(self.base_private_fields)
        if data.get("status") in ("draft", "active.tendering"):
            self.private_fields.add("bids")
