from openprocurement.tender.belowthreshold.tests.base import test_tender_below_organization


def get_award_data(self, **kwargs):
    data = {
        "suppliers": [test_tender_below_organization],
        "subcontractingDetails": "Details",
        "status": "pending",
        "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
    }
    if self.initial_data["procurementMethodType"] != "reporting":
        data["qualified"] = True
    data.update(kwargs)
    return data
