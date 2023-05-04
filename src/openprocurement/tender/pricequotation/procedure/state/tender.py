from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.pricequotation.constants import QUALIFICATION_DURATION
from openprocurement.tender.pricequotation.models.tender import Contract


class PriceQuotationTenderState(TenderState):
    contract_model = Contract

    def get_events(self, tender):
        status = tender["status"]

        if status == "active.tendering":
            if tender.get("tenderPeriod", {}).get("endDate"):
                yield tender["tenderPeriod"]["endDate"], self.tendering_end_handler

        yield from self.contract_events(tender)

        if status.startswith("active"):
            for award in tender.get("awards", ""):
                if award["status"] == 'pending':
                    check = calculate_tender_business_date(
                        dt_from_iso(award["date"]), QUALIFICATION_DURATION, tender, working_days=True
                    )
                    yield check.isoformat(), self.pending_award_handler(award)

    # handlers
    def tendering_end_handler(self, tender):
        handler = self.get_change_tender_status_handler("active.qualification")
        handler(tender)

        self.remove_draft_bids(tender)
        self.check_bids_number(tender)

    def pending_award_handler(self, award):
        def handler(tender):
            self.set_object_status(award, "unsuccessful")
            if any(a["status"] == 'cancelled' for a in tender.get("awards", "")):
                status_handler = self.get_change_tender_status_handler("unsuccessful")
                status_handler(tender)
            else:
                self.add_next_award()
                if tender["status"] == "active.awarded":
                    self.check_tender_status(tender)
        return handler

    # utils
    def check_bids_number(self, tender):
        if len(tender.get("bids", "")) == 0:
            self.get_change_tender_status_handler("unsuccessful")(tender)
        else:
            self.add_next_award()

    def check_tender_status(self, tender):
        last_award_status = tender["awards"][-1]["status"]
        if last_award_status == "unsuccessful":
            handler = self.get_change_tender_status_handler("unsuccessful")
            handler(tender)

        contract_statuses = {c["status"] for c in tender.get("contracts", "")}
        if (
            contract_statuses
            and "active" in contract_statuses
            and "pending" not in contract_statuses
        ):
            handler = self.get_change_tender_status_handler("complete")
            handler(tender)

    def add_next_award(self):
        request = get_request()
        tender = request.validated["tender"]
        if not tender.get("awardPeriod"):
            tender["awardPeriod"] = {}
        if not tender["awardPeriod"].get("startDate"):
            tender["awardPeriod"]["startDate"] = get_now().isoformat()

        awards = tender.get("awards", "")
        if not awards or awards[-1]["status"] not in ("pending", "active"):
            unsuccessful_award_bids = [
                a["bid_id"] for a in awards
                if a["status"] == "unsuccessful"
            ]
            bids = sorted([
                bid for bid in tender.get("bids", "")
                if bid["id"] not in unsuccessful_award_bids
            ], key=lambda bid: bid["value"]["amount"])
            if bids:
                bid = bids[0]
                award = Award(
                    {
                        "bid_id": bid["id"],
                        "status": "pending",
                        "date": get_now().isoformat(),
                        "value": bid["value"],
                        "suppliers": bid["tenderers"],
                    }
                )
                if "awards" not in tender:
                    tender["awards"] = []
                tender["awards"].append(
                    award.serialize()
                )
                request.response.headers["Location"] = request.route_url(
                    "{}:Tender Awards".format(tender["procurementMethodType"]),
                    tender_id=tender["_id"],
                    award_id=award["id"]
                )
            else:
                self.get_change_tender_status_handler("unsuccessful")(tender)
                return
        if tender["awards"][-1]["status"] == "pending":
            if tender["status"] != "active.qualification":
                if "endDate" in tender["awardPeriod"]:
                    del tender["awardPeriod"]["endDate"]
                self.get_change_tender_status_handler("active.qualification")(tender)
        else:
            if tender["status"] != "active.awarded":
                tender["awardPeriod"]["endDate"] = get_now().isoformat()
                self.get_change_tender_status_handler("active.awarded")(tender)
