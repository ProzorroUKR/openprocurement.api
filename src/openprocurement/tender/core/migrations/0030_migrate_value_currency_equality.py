# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.database import get_public_ts
from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.api.utils import get_now

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


TENDER_IDS = [
    "adc7b7456a8b455fbbf25398c172633e",
    "1df98a61b024438b8c70dbacb184e347",
    "5bc7fe5b190944c5b05b8da1d1a8ef22",
    "da30a3a0507b4fd68b71df0d2b650e33",
    "e396084bc87a48ff8578a6e8b4d80ccd",
    "a05fc90592d34a7a80e170ab96f781a4",
    "1b2c761646004ad2b29dab79c8bb7e7d",
    "60e3f90357304a67912b14807e43366a",
    "583cb29abe574964a749d1f70990694b",
    "bc212dd7d8b3428daf5f529d4b540dc1",
    "bc212dd7d8b3428daf5f529d4b540dc1",
    "969d5b2c81df4576870c9b3b0cb4fe18",
    "598a0b393bfb4b90a2e5dd1b480e65a7",
    "c12048c4c9ce4511897d78b29efb76a3",
    "6a348cae0ff9452b8d9cba99960faead",
    "33f24f59fdcd43e78ec03adc68f089fc",
    "22268339f01e41a5bfcf1cab20b47516",
    "37dc78121a2e4962b000641a9ad955ee",
    "88d8b58689d648979b9bf388f141c75a",
    "b2f5bebc8d37477e8d3f16b479377b24",
    "b0879613cc5f416b9884696f88861c81",
    "b0879613cc5f416b9884696f88861c81",
    "4d09ceff4c6f4945aa9fc604e7f88814",
    "46a575d5471f4fcdb08847eadac548c8",
    "f62080c2a5b64cd082a74d6ba54cafa2",
    "bd1ca237eb3c41b181d19fae2fd83274",
    "0adbcd0f0ed74b2fb7efd047f9a94904",
    "178bc17940cf4d388a9bac0d8f42cfbf",
    "89bb09ae523247c1b5f4e1a0fb4680ee",
    "8d05de94a60f4126886f91a7413aa7d9",
    "489b02c2a3c644eabf0741d27f8d87ec",
    "5a1104ead6354a4d8aa844fd91e296f7",
    "5625b72879f5454794411feef946ec2d",
    "1420bde75f5b47c7b988085b42045942",
    "a13a0ab0f9c04d95be13535698a88f6c",
    "c59791eb364a474a9e996ca68c6e1d2d",
]


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    tenders_collection = env["registry"].mongodb.tenders.collection

    log_every = 100000
    count = 0

    cursor = tenders_collection.find(
        {"_id": {"$in": TENDER_IDS}, "config.valueCurrencyEquality": True},
        {"config": 1},
        no_cursor_timeout=True,
    )

    cursor.batch_size(args.b)

    try:
        for tender in cursor:
            now = get_now()
            try:
                tenders_collection.find_one_and_update(
                    {"_id": tender["_id"]},
                    [
                        {
                            "$set": {
                                "config.valueCurrencyEquality": False,
                                "dateModified": now.isoformat(),
                                "public_modified": now.timestamp(),
                                "public_ts": get_public_ts(),
                            },
                        }
                    ],
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with valueCurrencyEquality field: updated {count} tenders")
            except OperationFailure as e:
                logger.warning(f"Skip updating tender {tender['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Successful migration: {migration_name}, results: {count}  tenders")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
