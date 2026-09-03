from openprocurement.tender.limited.constants import VALUE_AMOUNT_THRESHOLD_MAPPING


def reporting_cause_is_required(data):
    procedure_kind = data.get("procuringEntity", {}).get("kind")
    return all(
        [
            procedure_kind != "other",
            not data.get("procurementMethodRationale"),
            (
                data.get("value")
                and data["value"].get("amount")
                and data.get("mainProcurementCategory")
                and VALUE_AMOUNT_THRESHOLD_MAPPING.get(procedure_kind)
                and data["value"]["amount"]
                >= VALUE_AMOUNT_THRESHOLD_MAPPING[procedure_kind][data["mainProcurementCategory"]]
            ),
        ]
    )
