from openprocurement.api.adapters import ContentConfigurator
from openprocurement.agreement.core.constants import DEFAULT_TYPE


class BaseAgreementConfigurator(ContentConfigurator):

    name = "Base Agreement Configurator"
    model = None
    agreement_type = DEFAULT_TYPE
