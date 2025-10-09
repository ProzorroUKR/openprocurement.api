from openprocurement.api.application import Application

from .database_async import ContractCollection


def main(app: Application, *_) -> None:
    app.db.add_collection(
        ContractCollection.object_name,
        ContractCollection,
    )
