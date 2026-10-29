from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.contracting.core.procedure.serializers.contract import ContractBaseSerializer
from openprocurement.contracting.core.procedure.serializers.document import (
    ContractDocumentSerializer,
)


class TerminationDetailsSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ContractDocumentSerializer),
    }


class ContractContextSerializer(ContractBaseSerializer):
    """
    Keys are sorted so the JSON this is rendered into matches, byte-for-byte,
    the `sort_keys=True` reconstruction used to verify the terminationSignature
    (see EContractTerminationDetailsDocumentState.validate_termination_signature).
    """

    def serialize(self, data, **kwargs):
        return dict(sorted(super().serialize(data, **kwargs).items()))
