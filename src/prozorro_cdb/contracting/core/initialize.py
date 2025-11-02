from prozorro_cdb.api.application import Application

from .database import ContractCollection


def main(app: Application, *_) -> None:
    app.db.add_collection(
        ContractCollection.object_name,
        ContractCollection,
    )
