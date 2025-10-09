from aiohttp import web

from openprocurement.api.database_async import MongodbStore
from openprocurement.api.models_async.settings import DocStorageConfig


class Application(web.Application):
    db: MongodbStore
    doc_storage: DocStorageConfig
