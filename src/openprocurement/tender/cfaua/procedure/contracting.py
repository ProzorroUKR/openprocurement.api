from copy import deepcopy
from hashlib import sha512

from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import request_init_agreement
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.models.agreement import PostAgreement
from openprocurement.framework.core.procedure.utils import save_object


def get_additional_agreements_data(tender: dict, tender_agreement: dict) -> dict:
    active_contracts = [c for c in tender_agreement["contracts"] if c["status"] == "active"]
    return {
        "agreementType": CFA_UA,
        "tender_id": tender["_id"],
        "tender_token": sha512(tender["owner_token"].encode("utf-8")).hexdigest(),
        "owner": tender["owner"],
        "procuringEntity": tender["procuringEntity"],
        "contracts": active_contracts,
        "numberOfContracts": len(active_contracts),
        "mode": tender.get("mode"),
    }


def save_agreements_agreement(tender_agreement: dict) -> None:
    request = get_request()
    tender = get_tender()

    agreement = deepcopy(tender_agreement)
    agreement.update(get_additional_agreements_data(tender, tender_agreement))
    agreement = PostAgreement(agreement).serialize()
    agreement["config"] = {
        "restricted": tender["config"]["restricted"],
    }

    request_init_agreement(request, agreement, agreement_src={})
    save_object(request, "agreement", insert=True)
