from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.limited.procedure.serializers.cause import (
    CauseDetailsSerializer,
)


class LimitedTenderBaseSerializer(TenderBaseSerializer):
    serializers = {
        **TenderBaseSerializer.serializers,
        "causeDetails": CauseDetailsSerializer,  # TODO: remove after migration
    }
