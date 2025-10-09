from openprocurement.api.application import Application

from .database_async import AgreementCollection


def main(app: Application, *_) -> None:
    app.db.add_collection(
        AgreementCollection.object_name,
        AgreementCollection,
    )
