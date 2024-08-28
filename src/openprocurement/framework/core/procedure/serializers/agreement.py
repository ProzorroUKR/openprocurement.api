from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.framework.core.procedure.serializers.contract import (
    ContractSerializer,
)


class AgreementSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "_rev",
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
        "__parent__",
        "_attachments",
    }

    serializers = {
        "contracts": ListSerializer(ContractSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)


def test_serializer(obj, value):
    if value is False:
        return None
    return value


def restricted_serializer(obj, value):
    if value is None:
        return False
    return value


class AgreementConfigSerializer(BaseConfigSerializer):
    serializers = {
        "test": test_serializer,
        "restricted": restricted_serializer,
    }
