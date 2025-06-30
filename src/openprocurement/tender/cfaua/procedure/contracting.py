from copy import deepcopy
from hashlib import sha512

from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import request_init_agreement
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.models.agreement import PostAgreement
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.tender.cfaua.procedure.serializers.agreement import (
    AgreementSerializer,
)


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

    agreement_data = AgreementSerializer(agreement).data
    agreement_data.update(get_additional_agreements_data(tender, tender_agreement))
    agreement_data = clean_agreement(agreement_data)

    agreement = PostAgreement(agreement_data).serialize()
    agreement["config"] = {
        "restricted": tender["config"]["restricted"],
    }

    request_init_agreement(request, agreement, agreement_src={})
    save_object(request, "agreement", insert=True)


def clean_agreement(agreement: dict) -> dict:
    documents_delete_fields = {"confidentiality", "confidentialityRationale"}
    for doc in agreement.get("documents", ""):
        for field in documents_delete_fields:
            doc.pop(field, None)
    for field_name in ("signerInfo", "contract_owner"):
        agreement.get("procuringEntity", {}).pop(field_name, None)
    return agreement
