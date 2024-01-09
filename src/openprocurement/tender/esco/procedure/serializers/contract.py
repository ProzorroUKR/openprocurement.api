from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer, decimal_serializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


class ContractValueSerializer(BaseSerializer):
    serializers = {
        "amount": decimal_serializer,
        "amountPerformance": decimal_serializer,
        "yearlyPaymentsPercentage": decimal_serializer,
        "annualCostsReduction": ListSerializer(decimal_serializer),
        "amountNet": decimal_serializer,
    }


class ContractSerializer(BaseSerializer):
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }

    serializers = {
        "value": ContractValueSerializer,
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
