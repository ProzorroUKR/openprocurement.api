from hashlib import new

from openprocurement.api.procedure.serializers.base import BaseSerializer


class HiddenAuthorSerializer(BaseSerializer):
    public_fields = {"hash"}

    def get_hash(self, salt):
        identifier_id = self.raw.get("identifier", {}).get("id")
        if identifier_id:
            return new("md5", f"{identifier_id}_{salt}".encode(), usedforsecurity=False).hexdigest()
