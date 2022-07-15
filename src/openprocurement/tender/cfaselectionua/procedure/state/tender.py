from openprocurement.tender.core.procedure.state.tender import TenderState


class CFASelectionTenderState(TenderState):
    min_bids_number = 1

    def lots_qualification_events(self, tender):
        yield from ()  # no qualification events

    def lots_awarded_events(self, tender):
        yield from ()  # no awarded events

    def check_bids_number(self, tender):
        if tender.get("lots"):
            for lot in tender["lots"]:
                bid_number = self.count_lot_bids_number(tender, lot["id"])
                if bid_number < self.min_bids_number:
                    self.remove_auction_period(lot)
                    if lot["status"] == "active":
                        self.set_object_status(lot, "unsuccessful")

            # should be moved to tender_status_check ?
            if not set(i["status"] for i in tender["lots"]).difference({"unsuccessful", "cancelled"}):
                self.get_change_tender_status_handler("unsuccessful")(tender)

            elif max(self.count_lot_bids_number(tender, i["id"])
                     for i in tender["lots"] if i["status"] == "active") == 1:
                self.add_next_award()
        else:
            bid_number = self.count_bids_number(tender)
            if bid_number == 1:
                self.add_next_award()
            elif bid_number < self.min_bids_number:
                self.remove_auction_period(tender)
                self.get_change_tender_status_handler("unsuccessful")(tender)

    def calc_tender_value(self, tender: dict) -> None:
        if not all(i.get("value") for i in tender.get("lots", "")):
            return
        tender["value"] = {
            "amount": sum(i["value"]["amount"] for i in tender["lots"]),
            "currency": tender["lots"][0]["value"]["currency"],
            "valueAddedTaxIncluded": tender["lots"][0]["value"]["valueAddedTaxIncluded"]
        }

    def calc_tender_minimal_step(self, tender: dict) -> None:
        if not all(i.get("minimalStep") for i in tender.get("lots", "")):
            return
        tender["minimalStep"] = {
            "amount": min(i["minimalStep"]["amount"] for i in tender["lots"] if i.get("minimalStep")),
            "currency": tender["lots"][0]["minimalStep"]["currency"],
            "valueAddedTaxIncluded": tender["lots"][0]["minimalStep"]["valueAddedTaxIncluded"],
        }
