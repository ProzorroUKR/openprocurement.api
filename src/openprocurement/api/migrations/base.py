import os
from argparse import ArgumentParser

from openprocurement.api.constants import BASE_DIR


class MigrationArgumentParser(ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "-p",
            "--path",
            default=os.path.join(BASE_DIR, "etc/service.ini"),
            help="Path to service.ini file",
        )
        self.add_argument(
            "-b",
            "--batch-size",
            type=int,
            default=1000,
            help=(
                "Limits the number of documents returned in one batch. Each batch requires a round trip to the server."
            ),
        )
