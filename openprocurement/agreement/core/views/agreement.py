from openprocurement.agreement.core.resource import (
    AgreementsResource,
    agreements_resource
    )


@agreements_resource(
    name="Agreements",
    path="/agreements"
)
class APIAgreementsResource(AgreementsResource):
    """ Base agreement containder """


