from openprocurement.api.application import Application

from .database_async import TenderCollection


def main(app: Application, *_) -> None:
    app.db.add_collection(
        TenderCollection.object_name,
        TenderCollection,
    )
