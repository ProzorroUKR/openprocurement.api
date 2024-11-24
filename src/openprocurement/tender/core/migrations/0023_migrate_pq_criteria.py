# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from bson.decimal128 import Decimal128
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

NEW_CRITERION_DATA = {
    "title": "Технічні, якісні та кількісні характеристики предмету закупівлі",
    "description": "Учасники процедури закупівлі повинні надати у складі тендерних "
    "пропозицій інформацію та документи, які підтверджують відповідність "
    "тендерної пропозиції учасника технічним, якісним, кількісним та іншим "
    "вимогам до предмета закупівлі, установленим замовником",
    "classification": {"scheme": "ESPD211", "id": "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES"},
    "legislation": [
        {
            "version": "2024-04-19",
            "type": "NATIONAL_LEGISLATION",
            "identifier": {
                "uri": "https://zakon.rada.gov.ua/laws/show/922-19#Text",
                "id": "922-VIII",
                "legalName": "Закон України \"Про публічні закупівлі\"",
            },
            "article": "22.2.3",
        },
        {
            "version": "2023-10-31",
            "type": "NATIONAL_LEGISLATION",
            "identifier": {
                "uri": "https://zakon.rada.gov.ua/laws/show/1135-2023-%D0%BF#n24",
                "id": "1135-2023-п",
                "legalName": "Про внесення змін до постанов Кабінету Міністрів України "
                "від 14 вересня 2020 р. № 822 і від 12 жовтня 2022 р. № 1178",
            },
            "article": "2.1",
        },
    ],
    "source": "tenderer",
}

NEW_CRITERION_RG_DATA = {"description": "Підтверджується, що"}


# Function to handle and convert any fields that might require Decimal128
def convert_to_decimal128(value):
    try:
        return Decimal128(str(value))
    except:
        return value  # Return the value as-is if conversion fails


def update_criteria(criteria: list) -> list:
    if not criteria:
        return []

    for criterion in criteria:
        criterion.update(NEW_CRITERION_DATA)
        for rg in criterion.get("requirementGroups", ""):
            rg.update(NEW_CRITERION_RG_DATA)
            for req in rg.get("requirements", []):
                if "minValue" in req and isinstance(req["minValue"], dict) and "$numberDecimal" in req["minValue"]:
                    req["minValue"] = convert_to_decimal128(req["minValue"]["$numberDecimal"])

                if "maxValue" in req and isinstance(req["maxValue"], dict) and "$numberDecimal" in req["maxValue"]:
                    req["maxValue"] = convert_to_decimal128(req["maxValue"]["$numberDecimal"])

    return criteria


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Migrating PQ tenders from expected value to values field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "procurementMethodType": PQ,
            "criteria": {"$exists": True},
        },
        {"criteria": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:

            set_data = {"criteria": update_criteria(tender["criteria"])}

            collection.find_one_and_update({"_id": tender["_id"]}, {"$set": set_data})
            count += 1
            if count and count % log_every == 0:
                logger.info(f"Updating PQ tenders criteria: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating PQ tenders criteria: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
