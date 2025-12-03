from hashlib import sha512

from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


def tender_token_serializer(value: str) -> str:
    return sha512(value.encode("utf-8")).hexdigest()


class TenderCredentialsSerializer(BaseUIDSerializer):
    serializers = {
        "tender_token": tender_token_serializer,
    }
    public_fields = {
        "id",
        "owner",
        "tender_token",
    }

    def serialize(self, data: dict, **kwargs) -> dict:
        data = data.copy()
        data["tender_token"] = data.pop("owner_token")
        return super().serialize(data, **kwargs)
