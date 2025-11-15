from openprocurement.api.procedure.serializers.base import ListSerializer
from prozorro_cdb.api.serializers.base import BaseSerializer


class IdentifierSerializer(BaseSerializer):
    pass


class ContactPointSerializer(BaseSerializer):
    pass


class ClassificationSerializer(BaseSerializer):
    pass


class AddressClassificationSerializer(BaseSerializer):
    pass


class AddressSerializer(BaseSerializer):
    serializers = {
        "addressDetails": AddressClassificationSerializer,
    }


class OrganizationSerializer(BaseSerializer):
    serializers = {
        "identifier": IdentifierSerializer,
        "contactPoint": ContactPointSerializer,
        "additionalIdentifiers": ListSerializer(IdentifierSerializer),
        "additionalContactPoints": ListSerializer(ContactPointSerializer),
        "address": AddressSerializer,
    }


class SignerInfoSerializer(BaseSerializer):
    pass


class SupplierSerializer(OrganizationSerializer):
    serializers = {
        "identifier": IdentifierSerializer,
        "contactPoint": ContactPointSerializer,
        "additionalIdentifiers": ListSerializer(IdentifierSerializer),
        "additionalContactPoints": ListSerializer(ContactPointSerializer),
        "address": AddressSerializer,
        "signerInfo": SignerInfoSerializer,
    }


class BuyerSerializer(SupplierSerializer):
    pass


class ProcuringEntitySerializer(OrganizationSerializer):
    pass
