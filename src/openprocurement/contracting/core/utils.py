from logging import getLogger

from openprocurement.api.mask import mask_object_data
from openprocurement.api.mask_deprecated import mask_object_data_deprecated
from openprocurement.api.utils import error_handler
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.tender.core.procedure.utils import extract_path

LOGGER = getLogger("openprocurement.contracting.core")


def extract_contract_id(request):
    if request.matchdict and "contract_id" in request.matchdict:
        return request.matchdict.get("contract_id")

    path = extract_path(request)
    # extract tender id
    parts = path.split("/")
    if len(parts) < 5 or parts[3] != "contracts":
        return
    contract_id = parts[4]
    return contract_id


def extract_contract_doc(request):
    db = request.registry.mongodb.contracts
    contract_id = extract_contract_id(request)
    if contract_id:
        doc = db.get(contract_id)
        if doc is None:
            request.errors.add("url", "contract_id", "Not Found")
            request.errors.status = 404
            raise error_handler(request)

        mask_object_data_deprecated(request, doc)  # war time measures
        mask_object_data(request, doc, CONTRACT_MASK_MAPPING)

        return doc


class ContractTypePredicate:
    """Contract Route predicate."""

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "contractType = {}".format(self.val)

    phash = text

    def __call__(self, context, request):
        if request.contract_doc is not None:
            for access_details in request.contract_doc.get("access", []):
                if access_details["role"] in (AccessRole.SUPPLIER, AccessRole.BUYER):
                    contract_type = "eContract"
                    break
            else:
                contract_type = "contract"
            return contract_type == self.val
        return False
