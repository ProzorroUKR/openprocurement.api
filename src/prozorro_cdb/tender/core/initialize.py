from prozorro_cdb.api.application import Application

from .database import TenderCollection


def main(app: Application, *_) -> None:
    app.db.add_collection(
        TenderCollection.object_name,
        TenderCollection,
    )
