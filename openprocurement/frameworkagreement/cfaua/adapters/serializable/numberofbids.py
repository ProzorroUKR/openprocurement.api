# /src/openprocurement.tender.openua/openprocurement/tender/openua/models.py:382


class TenderNumberOfBids(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, *args, **kwargs):
        return len([bid for bid in self.context.bids if bid.status in ("active", "pending",)])
