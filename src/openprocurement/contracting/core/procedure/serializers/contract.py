from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class ContractBaseSerializer(BaseUIDSerializer):
    private_fields = {
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "tender_token",
        "owner_token",
        "bid_owner",
        "bid_token",
        "revisions",
        "public_modified",
        "is_public",
        "is_test",
        "config",
    }
