from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.api.utils import get_tender_by_id, request_init_tender
from openprocurement.api.procedure.context import get_tender


def restricted_serializer(obj, value):
    if value is None:
        # TODO:
        #  now we need to pull this value from tender config on contracting bridge contract creatiion
        #  when e-contracting will be enabled for all procedures:
        #    return False

        tender = get_tender()

        if not tender:
            request = get_request()
            contract = request.validated.get("contract") or request.validated.get("data")

            if not contract:
                return False

            tender = get_tender_by_id(request, contract["tender_id"], raise_error=False)

            if tender is None:
                return False

            request_init_tender(request, tender)
            tender_config = get_tender()

        return tender["config"]["restricted"]

    return value


class ContractConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restricted": restricted_serializer,
    }
