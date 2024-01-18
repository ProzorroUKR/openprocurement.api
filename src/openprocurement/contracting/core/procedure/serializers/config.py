from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.api.utils import get_tender_by_id, request_init_tender
from openprocurement.api.procedure.context import get_tender_config


def restricted_serializer(obj, value):
    if value is None:
        # TODO:
        #  now we need to pull this value from tender config on contracting bridge contract creatiion
        #  when e-contracting will be enabled for all procedures:
        #    return False

        tender_config = get_tender_config()

        if not tender_config:
            request = get_request()
            contract = request.validated.get("contract") or request.validated.get("data")
            tender = get_tender_by_id(request, contract["tender_id"], raise_error=False)

            if tender is None:
                return False

            request_init_tender(request, tender)
            tender_config = get_tender_config()

        return tender_config["restricted"]

    return value

class ContractConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restricted": restricted_serializer,
    }
