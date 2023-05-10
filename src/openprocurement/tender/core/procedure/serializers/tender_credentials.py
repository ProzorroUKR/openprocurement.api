from hashlib import sha512

from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer


class TenderCredentialsSerializer(BaseUIDSerializer):
    whitelist = {"_id", "owner", "owner_token"}

    @property
    def data(self) -> dict:
        data = super().data
        data["tender_token"] = sha512(data.pop("owner_token").encode("utf-8")).hexdigest()
        return data
