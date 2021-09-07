from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_request, get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.pricequotation.constants import QUALIFICATION_DURATION


class PriceQuotationTenderState(TenderState):

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
            award["status"] = 'unsuccessful'
            if any(a["status"] == 'cancelled' for a in tender.get("awards", "")):
                status_handler = self.get_change_tender_status_handler("unsuccessful")
                status_handler(tender)
            else:
                self.add_next_award(get_request())
                if tender["status"] == "active.awarded":
                    self.check_tender_status(tender)
        return handler

    # utils
    def check_bids_number(self, tender):
        if not any(i["status"] not in ("active", "unsuccessful")
                   for i in tender.get("cancellations", "")):
            if len(tender.get("bids", "")) == 0:
                tender["status"] = "unsuccessful"
            else:
                self.add_next_award(get_request())

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

    @staticmethod
    def add_next_award(request):
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
                tender["status"] = 'unsuccessful'
                return
        if tender["awards"][-1]["status"] == "pending":
            if "endDate" in tender["awardPeriod"]:
                del tender["awardPeriod"]["endDate"]
            tender["status"] = "active.qualification"
        else:
            tender["awardPeriod"]["endDate"] = get_now().isoformat()
            tender["status"] = "active.awarded"
