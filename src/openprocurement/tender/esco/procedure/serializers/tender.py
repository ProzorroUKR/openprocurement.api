from openprocurement.tender.core.procedure.serializers.base import ListSerializer, decimal_serializer
from openprocurement.tender.core.procedure.serializers.tender import TenderBaseSerializer
from openprocurement.tender.core.procedure.serializers.cancellation import CancellationSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from openprocurement.tender.core.procedure.serializers.qualification import QualificationSerializer
from openprocurement.tender.esco.procedure.serializers.award import AwardSerializer
from openprocurement.tender.esco.procedure.serializers.bid import BidSerializer
from openprocurement.tender.esco.procedure.serializers.contract import ContractSerializer
from openprocurement.tender.esco.procedure.serializers.lot import LotSerializer


class ESCOTenderSerializer(TenderBaseSerializer):
    serializers = {
        "bids": ListSerializer(BidSerializer),
        "qualifications": ListSerializer(QualificationSerializer),
        "cancellations": ListSerializer(CancellationSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "contracts": ListSerializer(ContractSerializer),
        "yearlyPaymentsPercentageRange": decimal_serializer,
        "minimalStepPercentage": decimal_serializer,
        "NBUdiscountRate": decimal_serializer,
        "lots": ListSerializer(LotSerializer),
        "awards": ListSerializer(AwardSerializer),
    }
