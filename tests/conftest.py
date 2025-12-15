import asyncio
import os
import uuid
from base64 import b64encode
from pathlib import Path
from typing import AsyncIterable, AsyncIterator
from urllib.parse import urlencode

import pytest
from aiohttp.pytest_plugin import AiohttpClient
from nacl.encoding import HexEncoder

from openprocurement.api.app import load_config
from prozorro_cdb.api.database.store import MongodbStore, get_mongodb
from prozorro_cdb.api.main import get_aiohttp_sub_app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def sub_app(event_loop):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_file_path = current_directory / Path("config.ini")

    global_config = {"here": current_directory, "__file__": str(config_file_path)}
    settings = load_config(config_file_path)

    return get_aiohttp_sub_app(global_config, **settings["app:main"])


@pytest.fixture(scope="function")
async def api(event_loop, sub_app, aiohttp_client) -> AsyncIterable[AiohttpClient]:
    api_client = await aiohttp_client(sub_app)

    yield api_client

    for collection in sub_app.db.collections.values():
        await collection.flush()

    sub_app.db.drop_instance()


@pytest.fixture(scope="function")
async def db() -> AsyncIterator[MongodbStore]:
    """Creates DB client and returns database."""

    db = get_mongodb()
    yield db

    # Cleanup database after test completed
    await db.client.drop_database(db)


def generate_test_doc_url(sub_app, doc_hash=None):
    doc_id = uuid.uuid4().hex
    doc_hash = doc_hash or "0" * 32
    signer = sub_app.doc_storage_config.service_key
    keyid = signer.verify_key.encode(encoder=HexEncoder)[:8].decode()
    msg = "{}\0{}".format(doc_id, doc_hash).encode()
    signature = b64encode(signer.sign(msg).signature)
    query = {"Signature": signature, "KeyID": keyid}
    return "{}/{}?{}".format(sub_app.doc_storage_config.service_url, doc_id, urlencode(query))
