from copy import deepcopy
import argparse
from logging import getLogger
from hashlib import sha512

from openprocurement.api.utils import context_unpack
from openprocurement.framework.electroniccatalogue.models import Agreement, Qualification, Framework
from openprocurement.framework.core.design import frameworks_all_view, qualifications_by_framework_id_view
from openprocurement.framework.core.utils import (
    get_framework_by_id,
    get_agreement_by_id,
    get_submission_by_id,
    get_doc_by_id,
    save_agreement,
    generate_agreementID,
    generate_id,
    apply_patch,
)
from openprocurement.api.utils import get_now
from pyramid.paster import bootstrap


LOGGER = getLogger("openprocurement.framework.core")


def ensure_agreement(request):
    db = request.registry.db
    framework_data = request.validated["framework_src"]
    agreementID = framework_data.get("agreementID")
    if agreementID:
        agreement = get_agreement_by_id(request, agreementID)
        request.validated["agreement_src"] = agreement
        request.validated["agreement"] = Agreement(agreement)
        request.validated["agreement"].__parent__ = request.validated["qualification"].__parent__
    else:
        agreement_id = generate_id()
        now = get_now()
        transfer = generate_id()
        transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
        agreement_data = {
            "id": agreement_id,
            "agreementID": generate_agreementID(get_now(), db, request.registry.server_id),
            "frameworkID": framework_data["_id"],
            "agreementType": framework_data["frameworkType"],
            "status": "active",
            "period": {
                "startDate": now,
                "endDate": framework_data.get("qualificationPeriod").get("endDate")
            },
            "procuringEntity": framework_data.get("procuringEntity"),
            "classification": framework_data.get("classification"),
            "additionalClassifications": framework_data.get("additionalClassifications"),
            "contracts": [],
            "owner": framework_data["owner"],
            "owner_token": framework_data["owner_token"],
            "mode": framework_data.get("type"),
            "dateModified": now,
            "date": now,
            "transfer_token": transfer_token,
            "frameworkDetails": framework_data.get("frameworkDetails"),
        }
        agreement = Agreement(agreement_data)

        request.validated["agreement_src"] = {}
        request.validated["agreement"] = agreement
        if save_agreement(request):
            LOGGER.info(
                "Created agreement {}".format(agreement_id),
                extra=context_unpack(
                    request,
                    {"MESSAGE_ID": "agreement_create"},
                    {"agreement_id": agreement_id,
                     "agreement_mode": agreement.mode},
                ),
            )

            framework_data_updated = {"agreementID": agreement_id}

            apply_patch(
                request, data=framework_data_updated, src=request.validated["framework_src"],
                obj_name="framework"
            )
            print(f"Create agreement {agreement_id} and updated framework")
            framework_data.update(framework_data_updated)
            LOGGER.info("Updated framework {} with agreementID".format(framework_data["_id"]),
                        extra=context_unpack(request, {"MESSAGE_ID": "qualification_patch"}))


def create_agreement_contract(db, request):
    qualification = request.validated["qualification"]
    framework = request.validated["framework"]
    agreement_data = get_agreement_by_id(request, framework.agreementID)
    submission_data = get_submission_by_id(request, qualification.submissionID)

    qualification_ids = [i["qualificationID"] for i in agreement_data.get("contracts", "")]
    if agreement_data["status"] != "active" or qualification.id in qualification_ids:
        return

    contract_id = generate_id()
    first_milestone_data = {
        "type": "activation",
        "documents": qualification.documents
    }
    contract_data = {
        "id": contract_id,
        "qualificationID": qualification.id,
        "status": "active",
        "suppliers": submission_data["tenderers"],
        "milestones": [first_milestone_data],
    }
    new_contracts = deepcopy(agreement_data.get("contracts", []))
    new_contracts.append(contract_data)
    print(f"Create add contract from qualification {qualification['id']} to agreement {agreement_data['id']}")
    apply_patch(request, data={"contracts": new_contracts}, src=agreement_data, obj_name="agreement")
    LOGGER.info("Updated agreement {} with contract {}".format(agreement_data["_id"], contract_id),
                extra=context_unpack(request, {"MESSAGE_ID": "qualification_patch"}))


def run(path_to_ini_file):
    with bootstrap(path_to_ini_file) as env:
        db = env["registry"].db
        request = env["request"]
        request.validated = {}
        for i in frameworks_all_view(db, include_docs=True):
            framework_data = get_framework_by_id(request, i.id)
            if not framework_data:
                continue
            request.validated["framework_src"] = framework_data
            framework = request.validated["framework"] = Framework(framework_data)
            print(f"Get framework {i.id}")

            if framework.status != "active":
                continue
            for j in qualifications_by_framework_id_view(db, startkey=[framework.id, None], endkey=[framework.id, {}]):
                qualification_data = get_doc_by_id(db, "Qualification", j.id)
                qualification = Qualification(qualification_data)
                request.context = qualification
                request.validated["qualification_src"] = qualification_data
                request.validated["qualification"] = qualification
                if qualification["status"] != "active":
                    continue
                ensure_agreement(request)
                create_agreement_contract(db, request)
            print('\n\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Path to service.ini file")
    args = parser.parse_args()
    path_to_ini_file = args.p if args.p else "etc/service.ini"
    run(path_to_ini_file)
