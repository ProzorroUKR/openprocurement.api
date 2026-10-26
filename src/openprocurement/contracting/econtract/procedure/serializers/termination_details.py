from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.contracting.core.procedure.serializers.document import (
    ContractDocumentSerializer,
)


class TerminationDetailsSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ContractDocumentSerializer),
    }


class ContractContextSerializer(BaseUIDSerializer):
    """
    Keys are sorted so the JSON this is rendered into matches, byte-for-byte,
    the `sort_keys=True` reconstruction used to verify the terminationSignature
    (see EContractTerminationDetailsDocumentState.validate_termination_signature).

    No public_fields restriction for now - the signed payload includes the
    whole contract. May be narrowed down to a specific field list later.
    """

    def serialize(self, data, **kwargs):
        return dict(sorted(super().serialize(data, **kwargs).items()))
