#!/usr/bin/env python
import datetime
from time import sleep

from gevent import monkey

from openprocurement.api.utils import parse_date, get_now
from openprocurement.framework.core.utils import calculate_framework_date, SUBMISSION_STAND_STILL_DURATION

monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from openprocurement.api.constants import BASE_DIR
from pyramid.paster import bootstrap

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


ids = [
    "6148c89fde3d469e81ff82e8f4bafd0e",
    "056ee06aa6544b5c942de28a698fa375",
    "1dc41113143f434495e3863b848cea2d",
    "d57e70464d8b4c9781190a69f3f423b4",
    "75061076e2d540f1bc08b3a3807dbc46",
    "387922a78fb84baf8d342aa0a115df1b",
    "80ec75d3e4cb4134b555a7d8877352e4",
    "25a79377dcb7445caad44891b94e81eb",
    "340f220f5db241279fc44ee375774625",
    "6a843942f3b54d8d9ac9d7811ac664d2",
    "0817163d5d7f4f58bd46037f0d5ec051",
    "eb2c15dc61cc4314afec490bc8a9de78",
    "9884e89c8f1442d5b8d0accf54aabae2",
    "a0d66f05097448d5a6c43e03a476c7a9",
    "455a6c22cefe4be999b3f502fad944c7",
    "fedaceb4167d4a8c81447b815e1856eb",
    "ec38e4aaaa0f4e0facc3ebb53366b4ab",
    "e1ae850115624f83987e2c9071a4af55",
    "9d2db9fa24fa40819f50f85094ed6b29",
    "cca3539a2719407eb2ba440d6ad8f557",
    "ca4aa5a2f3114939a62b5662d7db5dee",
    "f4edba9af06241e387d9216673159bc8",
    "bde213ab19eb4efaacb9af4821365084",
    "fc2011aee62342349560fa77534b3f0d",
    "dc0a76c64ea84b148da94754689427cb",
    "766118ea7e454730bc0891d51f58f61e",
    "2813c37ad4dc433e9c3ba6a2ed4793fc",
    "0bdeac0913a74346818b5b847c00b66c",
    "857e295cdffb439fb7771b6aad61ad94",
    "7f70642384fe406984e8fb6e6e5689f0",
    "b94b22b14617478a9e458b988616ff63",
    "712160b4e4e0445fa4b7586f3af31a31",
    "c6465b70b3cb4d8c8cc50bff17f2cd1b",
    "449532c325614b59b938f2b17db0c25b",
    "b80f9eb2e17449718f8a3136975fbf17",
    "92e49fa487da40b3ab080b030f8a2b5d",
    "0772eee7fe414f29b7ec8cbde30b5b9e",
    "d282db9a2941440b94dd29c6e9672ff2",
    "22e30181246349b59054dd6ca5262c63",
    "e748d4b3a04a460bbd00115d9e4e72c8",
    "965f72b69bbb4f6c8cda3914584f017d",
    "94a2ea7c61f148d1b7dfea778f643006",
    "38cb84e1db414d54bf55f9110533d284",
    "3238d3a0e980483ebd56cfb4345d6489",
    "1d1bd18a66f840a98c192ef70e8b11bb",
    "54aa1929c57747179fd7c1af26d2a183",
    "233a7811b71a484b9ebdd62ba9a2e2bf",
    "7e1a9d1696264639a6807357da569ddb",
    "dfd25964223b4cf0ac3c70b6a80ab85c",
    "237c9091ec294a4f9ee0eaa512c5e8ac",
    "c58e52fb9b57450ba2fdc61efdc23847",
    "c42ff4b075ea4a33a54de644eaa481f2",
    "b49d9226f6c14c9eb1088ae0f7b97cfd",
    "f8b8317e7cfc4272b9ef4bde1718a038",
    "d68a81e0e2fb4605a5464de595a28132",
    "f325e30686f24e17843875e88c1df49f",
    "6b2638bc2a804f5bb3eed7c68ffb517b",
    "907f6fa610d34001845476df3e7a7649",
    "992ad651919045a5ac0397e95c0c0d67",
    "19990219337e4c18b74588f1e24cdc0e",
    "32f88758623945c18e0868a5b509a523",
    "148ebb334a9c4852be2cf5e11279df51",
    "a175440f218740a4a1f74d79b35a869b",
    "4a92234c02cf4abaa3c33723e04a6b8a",
    "d83a59ee1ebf4fd185d258e665fbab40",
    "81eac79718024681a8548312d427a691",
    "da564cc24bd0455f94fccb6d10b35136",
    "3ac329723907451386adf38b6c821308",
    "afcfa198168248798bb059ecfb4f9df1",
    "2676945ff1f4427291c7d7f50657064e",
    "8212f7d61d5c498da7d5cdf7e0832621",
    "b6965448e5504c1abe30f6f8dcd8c244",
    "b3326c5a8f8b4413ac436a4940d3220f",
    "8f7d0c1c150e46b887f4ea5bbb6afc8e",
    "7792af6ad0f940f789c0464c6db801bd",
    "06f9a31c3acb49e49856ed6b96412d10",
    "35fe8ec435874113bef5fb166db95cb6",
    "4b4bdfeb5eb44ae7920df61e95367ce7",
    "6557e141256b48848d2441d2369a2a2c",
    "38a38a9dc5d94cd9824b515c37ee6ea6",
    "1f8405106eee4841a7c1f67ce13f7e46",
    "3acff59fa5ec448a97ee60fe60a465e2",
    "618ae93a871d4f6bbbe77b1c0179ef57",
    "d84bad5a27c44a969408dbb78554667b",
    "d3a21e1ef19c4899b5c97b7c4468d4d7",
    "8856f5e357c046169c64cd6ae8da6ca6",
    "a323b8ca960b41ca9becd036ec9bc38f",
    "bbf822918f3440f9b3b3c98eae0df29e",
    "0e8375330d1f4b10a64746e509c7ac02",
    "3a37bcbda72545e2a6d7a0fd1f84f40b",
    "c3eab1689199439691bc340245ab1705",
    "6f0f49b9d7e9487f96e2bb882a367b60",
    "a6cc2294e6394ec2a469948dc86e5df0",
    "2ddc88b8239f46ababe862fb6a731dd1",
]

ids = [
    "bc2a5d79f29d42dab1a4d503ff4f65eb"
]

EXTEND_QUAL_PERIOD_DURATION = 365

def run(env):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.frameworks.collection

    logger.info("Updating frameworks")

    count = 0

    cursor = collection.find(
        {"_id": {"$in": ids}},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for framework in cursor:
            new_qual_period_end_date = parse_date(
                framework["qualificationPeriod"]["endDate"]
            ) + datetime.timedelta(days=EXTEND_QUAL_PERIOD_DURATION)

            new_period_end_date = calculate_framework_date(
                new_qual_period_end_date,
                datetime.timedelta(days=-SUBMISSION_STAND_STILL_DURATION),
                framework,
            )

            now = get_now()

            collection.find_one_and_update(
                {"_id": framework["_id"], "_rev": framework["_rev"]},
                [
                    {
                        "$set": {
                            "qualificationPeriod.endDate": new_qual_period_end_date.isoformat(),
                            "period.endDate": new_period_end_date.isoformat(),
                            "dateModified": now.isoformat(),
                            "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                        },
                    },
                ],
            )
            count += 1
            logger.info(f"Updating framework {framework['_id']}: {now}")

            sleep(0.000001)
    finally:
        cursor.close()

    logger.info(f"Updating frameworks: updated {count} frameworks")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        default=os.path.join(BASE_DIR, "etc/service.ini"),
        help="Path to service.ini file",
    )
    parser.add_argument(
        "-b",
        type=int,
        default=1000,
        help=(
            "Limits the number of documents returned in one batch. Each batch "
            "requires a round trip to the server."
        )
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env)
