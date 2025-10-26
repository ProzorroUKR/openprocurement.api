from aiohttp import web

from prozorro_cdb.api.database.store import MongodbStore
from prozorro_cdb.api.settings import DocStorageConfig


class Application(web.Application):
    db: MongodbStore
    doc_storage: DocStorageConfig
