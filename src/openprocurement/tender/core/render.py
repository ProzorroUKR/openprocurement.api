from openprocurement.api.render import env, HUMAN_FILTERS
from collections import defaultdict
import standards

pm_types = standards.load("codelists/tender/tender_procurement_method_type.json")
pm_types = {k: v["name_uk"] for k, v in pm_types.items()}

categories = standards.load("codelists/tender/tender_main_procurement_category.json")
categories = {k: v["name_uk"] for k, v in categories.items()}


HUMAN_FILTERS.update(
    procurementMethodType=lambda v: pm_types[v],
    mainProcurementCategory=lambda v: categories[v],
)


def render_tender_txt(data):
    items_numbers = {}
    for n, item in enumerate(data["items"], start=1):
        items_numbers[item["id"]] = n

    lots_numbers = {}
    for n, lot in enumerate(data.get("lots", ""), start=1):
        lots_numbers[lot['id']] = n

    data.update(
        items_numbers=items_numbers,
        lots_numbers=lots_numbers,
    )

    # render
    template = env.get_template("tender.txt")
    return template.render(data)


