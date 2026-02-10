from factory import Factory, Faker, SubFactory
from factory.fuzzy import FuzzyChoice

from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from prozorro_cdb.api.database.schema.organization import (
    Address,
    Buyer,
    ContactPoint,
    Identifier,
    Organization,
    ProcuringEntity,
    Supplier,
)


class IdentifierFactory(Factory):
    class Meta:
        model = Identifier

    id = Faker("passport_number")
    scheme = "UA-EDR"


class AddressFactory(Factory):
    class Meta:
        model = Address

    streetAddress = Faker("street_address")
    postalCode = Faker("postcode")
    countryName = Faker("country")


class ContactPointFactory(Factory):
    class Meta:
        model = ContactPoint

    name = Faker("name")
    email = Faker("email")
    telephone = Faker("phone_number")
    faxNumber = Faker("phone_number")
    url = Faker("url")


class OrganizationFactory(Factory):
    class Meta:
        model = Organization

    name = Faker("name")
    identifier = SubFactory(IdentifierFactory)
    address = SubFactory(AddressFactory)
    contactPoint = SubFactory(ContactPointFactory)


class BuyerFactory(OrganizationFactory):
    class Meta:
        model = Buyer

    kind = FuzzyChoice(ProcuringEntityKind)
    signerInfo = None


class SupplierFactory(OrganizationFactory):
    class Meta:
        model = Supplier

    scale = Faker("random_element", elements=["micro", "sme", "large"])
    signerInfo = None


class ProcuringEntityFactory(OrganizationFactory):
    class Meta:
        model = ProcuringEntity

    kind = FuzzyChoice(ProcuringEntityKind)
