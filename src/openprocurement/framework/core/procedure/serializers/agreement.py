from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import (
    BaseConfigSerializer,
    none_is_false_serializer,
)
from openprocurement.framework.core.procedure.serializers.contract import (
    ContractSerializer,
)


class AgreementSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "public_modified",
        "public_ts",
        "is_public",
        "is_test",
        "config",
        "frameworkDetails",
        "attachments",
    }

    serializers = {
        "contracts": ListSerializer(ContractSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)


def has_items_serializer(value):
    request = get_request()
    if value is None:
        agreement_patch = request.validated.get("agreement")
        agreement_post = request.validated.get("data")
        agreement = agreement_patch or agreement_post
        return bool(agreement.get("items"))
    return value


class AgreementConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restricted": none_is_false_serializer,
    }
