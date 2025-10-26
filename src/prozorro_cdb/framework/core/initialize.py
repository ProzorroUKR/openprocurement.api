from prozorro_cdb.api.application import Application

from .database import AgreementCollection


def main(app: Application, *_) -> None:
    app.db.add_collection(
        AgreementCollection.object_name,
        AgreementCollection,
    )
