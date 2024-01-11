from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import init_object
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.api.utils import get_tender_by_id
from openprocurement.tender.core.procedure.context import get_tender_config
from openprocurement.tender.core.procedure.serializers.config import TenderConfigSerializer


def restricted_serializer(obj, value):
    if value is None:
        tender_config = get_tender_config()

        if not tender_config:
            request = get_request()
            contract = request.validated.get("contract") or request.validated.get("data")
            tender = get_tender_by_id(request, contract["tender_id"], raise_error=False)

            if tender is None:
                return False

            init_object("tender", tender, config_serializer=TenderConfigSerializer)
            tender_config = get_tender_config()

        return tender_config["restricted"]

    return value

class ContractConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restricted": restricted_serializer,
    }
