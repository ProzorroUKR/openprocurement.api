from copy import deepcopy

from openprocurement.api.constants import OCID_PREFIX, ROUTE_PREFIX
from openprocurement.api.context import get_request

tender_status_choices = (
    "planning",
    "planned",
    "active",
    "cancelled",
    "unsuccessful",
    "complete",
    "withdrawn",
)

award_criteria_choices = (
    "priceOnly",
    "costOnly",
    "qualityOnly",
    "ratedCriteria",
    "lowestCost",  # this and all below are deprecated since 1.1
    "bestProposal",
    "bestValueToGovernment",
    "singleBidOnly",
)


def identifier_str(i):
    return f"{i['scheme']} {i['id']}"


def absolute_url(url):
    if url.startswith("/"):
        request = get_request()
        url = f"{request.application_url}{ROUTE_PREFIX}{url}"
    return url


def convert_documents(documents, lot_id=None, tender=None):
    latest_versions = {}
    for d in documents:
        if d.get("confidentiality") == "buyerOnly":
            continue

        if lot_id:
            if d.get("documentOf") == "lot" and d.get("relatedItem") != lot_id:
                continue

            item_lot_ids = {i["relatedLot"] for i in tender.get("items") if "relatedLot" in i}
            if d.get("documentOf") == "item" and d.get("relatedItem") not in item_lot_ids:
                continue

        doc_id = d["id"]
        if doc_id not in latest_versions or latest_versions[doc_id]["dateModified"] < d["dateModified"]:
            latest_versions[doc_id] = {
                "id": d["id"],
                "title": d.get("title"),
                "title_en": d.get("title_en"),
                "url": absolute_url(d["url"]),
                "datePublished": d["datePublished"],
                "dateModified": d["dateModified"],
                "format": d["format"],
                "language": d.get("language"),
            }
    return list(latest_versions.values())


def convert_milestones(milestones, lot_id=None):
    r = [
        {
            "id": m["id"],
            "title": m["title"],
            "description": m.get("description"),
            "type": m["type"],
            "code": m.get("code"),
            "dueDate": m.get("dueDate"),
            "dateMet": m.get("dateMet"),
            "dateModified": m.get("dateModified"),
            "status": m.get("status"),
        }
        for m in milestones
        if m.get("relatedLot") is None or m.get("relatedLot") == lot_id
    ]
    return r


def convert_value(v):
    if v:
        r = {
            "amount": v["amount"],
            "currency": v["currency"],
        }
        return r


def convert_items(items, lot_id=None):
    r = [
        {
            "id": i.get("id", str(n)),
            "description": i["description"],
            "classification": i.get("classification"),
            "additionalClassifications": i.get("additionalClassifications"),
            "unit": {"name": i["unit"]["name"]} if "name" in i.get("unit", "") else None,
            "quantity": i.get("quantity"),
        }
        for n, i in enumerate(items)
        if lot_id is None or i.get("relatedLot") == lot_id
    ]
    return r


def convert_contracts(contracts, award_ids=None):
    r = [
        {
            "id": c["id"],
            "awardID": c["awardID"],
            "status": c["status"],
            "value": convert_value(c.get("value")),
            "items": convert_items(c["items"]) if "items" in c else None,
            "dateSigned": c.get("dateSigned"),
            "documents": convert_documents(c.get("documents", "")),
        }
        for c in contracts
        if award_ids is None or c["awardID"] in award_ids
    ]
    return r


def convert_awards(awards, tender, lot_id=None):
    r = [
        {
            "id": a["id"],
            "title": a.get("title"),
            "description": a.get("description"),
            "status": a["status"],
            "date": a["date"],
            "value": convert_value(a["value"]),
            "suppliers": [
                (
                    {
                        "id": identifier_str(a["suppliers"][0]["identifier"]),
                        "name": a["suppliers"][0]["name"],
                    }
                    if "suppliers" in a
                    else {
                        "id": a["bid_id"],
                        "name": [b for b in tender["bids"] if b["id"] == a["bid_id"]][0]["tenderers"][0]["name"],
                    }
                )
            ],
            "items": convert_items(tender["items"], lot_id=lot_id),
            "documents": convert_documents(a.get("documents", "")),
        }
        for a in awards
        if lot_id is None or a.get("lotID") == lot_id
    ]
    return r


def filter_bids_by_lot(bids, lot_id=None):
    if lot_id is None:
        return bids
    else:
        # TODO: filter documents if documentOf = lot or item with relatedLot
        result = []
        for b in bids:
            for lv in b.get("lotValues", ""):
                if lot_id == lv["relatedLot"]:
                    b_copy = deepcopy(b)
                    # value & date
                    b_copy["date"] = lv.get("date") or b.get("date")  # we have a bug causes lotValues.date missed
                    value = lv.get("value")
                    if value:
                        b_copy["value"] = value
                    result.append(b_copy)
        return result


def parties_from_bids(tender, bids, lot_id=None):
    r = [
        {
            "id": b["id"],
            "name": b["tenderers"][0]["name"],
            "identifier": b["tenderers"][0]["identifier"],
            "address": b["tenderers"][0]["address"],
            "contactPoint": b["tenderers"][0].get("contactPoint"),
        }
        for b in filter_bids_by_lot(bids, lot_id)
        if "tenderers" in b
    ]
    return r


def prepare_release(plan, tender, lot=None):
    lot = lot or {}
    lot_id = lot['id'] if lot else None
    release_id = tender['id']
    if lot_id:
        release_id += f"-{lot_id}"

    parties = [
        {
            "id": identifier_str(tender["procuringEntity"]["identifier"]),
            "name": tender["procuringEntity"]["name"],
            "identifier": tender["procuringEntity"]["identifier"],
            "address": tender["procuringEntity"]["address"],
            "contactPoint": tender["procuringEntity"].get("contactPoint"),
        }
    ]
    parties.extend(parties_from_bids(tender, tender.get("bids", ""), lot_id=lot_id))
    tender_status = lot.get("status") or tender["status"]
    documents = convert_documents(tender.get("documents", ""), lot_id=lot_id, tender=tender)
    awards = convert_awards(tender.get("awards", ""), tender, lot_id=lot_id)

    r = {
        "ocid": f"{OCID_PREFIX}-{release_id}",
        "id": release_id,
        "date": plan["dateCreated"] if plan else tender["dateCreated"],
        "tag": ["tender"],
        # planning planningUpdate, tender, tenderAmendment, tenderUpdate, tenderCancellation, award, awardUpdate, awardCancellation, contract, contractUpdate, contractAmendment, implementation, implementationUpdate, contractTermination, compiled
        "initiationType": "tender",
        "parties": parties,
        "buyer": {
            "id": identifier_str(tender["procuringEntity"]["identifier"]),
            "name": tender["procuringEntity"]["name"],
        },
        "tender": {
            "id": tender["id"],
            "title": lot.get("title") or tender["title"],
            "title_en": lot.get("title_en") or tender.get("title_en"),
            "description": lot.get("description") or tender.get("description", ""),
            "description_en": lot.get("description_en") or tender.get("description_en", ""),
            "status": tender_status if tender_status in tender_status_choices else "active",
            "procuringEntity": {
                "id": identifier_str(tender["procuringEntity"]["identifier"]),
                "name": tender["procuringEntity"]["name"],
            },
            "items": convert_items(tender["items"], lot_id=lot_id),
            "value": convert_value(lot.get("value") or tender.get("value")),
            # "minValue": tender["minValue"], TODO: hm?
            "procurementMethod": tender["procurementMethod"],
            # "procurementMethodDetails": tender.get("procurementMethodDetails", ""),
            "procurementMethodRationale": tender.get("procurementMethodRationale", ""),  # don't expect it there
            "mainProcurementCategory": tender.get("mainProcurementCategory"),
            # "additionalProcurementCategories": [],  # Not Implemented
            "awardCriteria": (
                tender["awardCriteria"]
                if tender.get("awardCriteria") in award_criteria_choices  # TODO:  awardCriteria can be missing at all
                else "ratedCriteria"
            ),
            "awardCriteriaDetails": tender.get("awardCriteriaDetails"),
            "submissionMethod": [tender["submissionMethod"]] if "submissionMethod" in tender else None,
            # "submissionMethodDetails": tender.get("submissionMethodDetails", "")  # better not
            "tenderPeriod": tender.get("tenderPeriod"),
            "enquiryPeriod": (
                {
                    "startDate": tender["enquiryPeriod"].get("startDate"),
                    "endDate": tender["enquiryPeriod"].get("endDate"),
                }
                if "enquiryPeriod" in tender
                else tender.get("tenderPeriod")
            ),
            "hasEnquiries": any(
                complaint["type"] == "claim"
                for complaint in tender.get("complaints", "")
                if lot_id is None or complaint.get("relatedLot") is None or complaint.get("relatedLot") == lot_id
            ),
            "eligibilityCriteria": tender.get("eligibilityCriteria"),  # good luck ;)
            "awardPeriod": tender.get("awardPeriod"),
            "contractPeriod": tender.get("contractPeriod"),  # only in cfaua
            "numberOfTenderers": len(tender.get("bids", "")),
            "tenderers": [
                {
                    "id": b["id"],
                    "name": b["tenderers"][0]["name"],
                }
                for b in filter_bids_by_lot(tender.get("bids", ""), lot_id)
                if "tenderers" in b
            ],
            "documents": documents,
            # TODO should include bid documents as well?
            "milestones": convert_milestones(tender.get("milestones", ""), lot_id=lot_id),
            "amendments": [],  # Not implemented
        },
        "awards": awards,
        "contracts": convert_contracts(tender.get("contracts", ""), award_ids=[a["id"] for a in awards]),
    }
    if plan:
        planning = {
            "rationale": plan.get("rationale"),
            "documents": convert_documents(plan.get("documents", "")),
            "milestones": convert_milestones(plan.get("milestones", "")),
        }
        budget = plan.get("budget")
        if budget:
            planning["budget"] = {
                "id": plan["budget"]["id"],
                "description": plan["budget"]["description"],
                "amount": convert_value(plan["budget"]),
                # "projectID": "The name of the project through which this contracting process is funded",
                # "project": "An external identifier for the project",
                # "uri": "A URI pointing directly to a machine-readable record about the budget..",
            }
            project = budget.get("project")
            if project:
                if project_id := project.get("id"):
                    planning["budget"]["projectID"] = project_id

                project_name = project.get("name") or project.get("name_en")
                if project_name:
                    planning["budget"]["project"] = project_name
        r["planning"] = planning

    bids = tender.get("bids")
    if bids:
        bids = filter_bids_by_lot(bids, lot_id)
        if bids:
            bid_dates = [b["date"] for b in bids if "date" in b]
            r["bids"] = {
                "statistics": [
                    {
                        "id": "1",
                        "measure": "validBids",
                        "value": len(bids),
                        "date": max(bid_dates) if bid_dates else None,
                        "notes": "This statistic covers the total number of unique bids received that were considered "
                        "valid against relevant criteria.",
                    },
                ],
                "details": [convert_bid(b, lot_id=lot_id, tender=tender) for b in bids],
            }

    return r


def convert_bid(b, lot_id=None, tender=None):
    bid_status = b.get("status")
    # valid statuses are https://extensions.open-contracting.org/en/extensions/bids/master/codelists/#bidStatus.csv
    #  invited, pending, valid, disqualified, withdrawn
    # https://prozorro-api-docs.readthedocs.io/uk/master/standard/bid.html#schema
    # draft active invalid invalid.pre-qualification deleted pending
    if "invalid" in bid_status:
        status = "disqualified"
    elif bid_status == "active":
        status = "valid"
    elif bid_status == "deleted":  # we filter this out  earlier
        status = "withdrawn"
    else:
        status = "pending"
    r = {
        "id": b["id"],
        "date": b.get("date"),
        "status": status,
        "identifiers": [
            {
                "id": t["identifier"]["id"],
                "scheme": t["identifier"]["scheme"],
            }
            for t in b.get("tenderers", "")
        ],
        "value": convert_value(b.get("value")),
        "tenderers": [
            {
                "id": b["id"],
                "name": t["name"],
            }
            for t in b.get("tenderers", "")
        ],
    }
    # documents
    documents = []
    for key in ("documents", "financialDocuments", "eligibilityDocuments", "qualificationDocuments"):
        if key in b:
            documents.extend(convert_documents(b[key], lot_id=lot_id, tender=tender))
    r["documents"] = documents
    return r


def remove_nones(data):
    for k, v in list(data.items()):
        if v is None:
            del data[k]
        elif isinstance(v, str):
            if not v:
                del data[k]
        elif isinstance(v, dict):
            remove_nones(v)
            if not v:
                del data[k]
        elif isinstance(v, list):
            for e in v:
                if isinstance(e, dict):
                    remove_nones(e)
            if not v:
                del data[k]


def ocds_format_tender(*_, tender, tender_url, plan=None):
    releases = []
    if "lots" in tender:
        for l in tender["lots"]:
            releases.append(prepare_release(plan, tender, lot=l))
    else:
        releases.append(prepare_release(plan, tender))

    result = {
        "uri": f"{tender_url}?opt_schema=OCDS-1.1",
        "version": "1.1",
        "extensions": [
            "https://raw.githubusercontent.com/open-contracting-extensions/ocds_bid_extension/master/extension.json",
        ],
        "publisher": {
            "name": tender["procuringEntity"]["name"],
        },
        "publishedDate": tender["dateModified"],
        "releases": releases,
    }
    remove_nones(result)
    return result
