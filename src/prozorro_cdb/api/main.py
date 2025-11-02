# pylint: disable=wrong-import-position
import os

os.environ["NO_GEVENT_MONKEY_PATCH"] = "🚫🐒🚫🐒🚫🐒🚫🐒🚫🐒🚫🐒🚫"
os.environ["NO_SUB_APP_ROUTE_PREFIX"] = "yes"

from aiohttp import web
from aiohttp_pydantic import oas
from aiohttp_wsgi import WSGIHandler
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey

from openprocurement.api.app import load_callable, load_config, load_pyproject
from openprocurement.api.constants import MAIN_ROUTE_PREFIX
from prozorro_cdb.api.auth import get_login_middleware
from prozorro_cdb.api.database.store import MongodbStore
from prozorro_cdb.api.handlers.base import get_version, ping
from prozorro_cdb.api.middlewares import (
    access_logger_middleware,
    context_middleware,
    convert_response_to_json,
    db_session_middleware,
    error_middleware,
    jsonp_and_pretty_middleware,
)
from prozorro_cdb.api.settings import DocStorageConfig


def get_sub_app(global_config, **settings):
    # pylint: disable=import-outside-toplevel
    from openprocurement.api.app import main as pyramid_main

    global_settings = load_config(global_config["__file__"])
    trans_logger_settings = global_settings.get("filter:translogger") or {}
    trans_logger_disabled = trans_logger_settings.get("set_logger_level", "WARNING") == "WARNING"

    middlewares = []
    if not trans_logger_disabled:
        middlewares.append(access_logger_middleware)  # should be the first and the last to better track time

    auth_file = settings["auth.file"].replace("%(here)s", global_config["here"])
    middlewares.extend(
        [
            jsonp_and_pretty_middleware,  # last when we return response
            get_login_middleware(auth_file),  # should be before context_middleware
            context_middleware,
            db_session_middleware,
            error_middleware,
            convert_response_to_json,
        ]
    )

    # init app
    sub_app = web.Application(middlewares=middlewares)
    sub_app["project_info"] = project_info = load_pyproject()  # load info from pyproject.toml

    # add swagger docs
    oas.setup(
        sub_app,
        title_spec="Prozorro CDB API",
        security={"APIKeyHeader": {"type": "apiKey", "in": "header", "name": "Authorization"}},
        version_spec=project_info["project"]["version"],
        url_prefix="/doc",
    )

    # database
    sub_app.db = mongodb = MongodbStore.create_instance(settings)

    # add routes
    sub_app.router.add_get("/version", get_version, allow_head=False)
    sub_app.router.add_get("/ping", ping, allow_head=False)

    # docs storage
    signing_key = settings.get("dockey", "")
    signer = SigningKey(signing_key.encode(), encoder=HexEncoder) if signing_key else SigningKey.generate()
    verifier = signer.verify_key

    keyring = {verifier.encode(encoder=HexEncoder)[:8].decode(): verifier}
    doc_keys = settings.get("dockeys", "")
    for doc_key in doc_keys.split("\0"):
        if doc_key:
            keyring[doc_key[:8]] = VerifyKey(doc_key.encode(), encoder=HexEncoder)

    sub_app.doc_storage_config = DocStorageConfig(
        service_url=settings.get("docservice_url"),
        dep_service_url=settings.get("dep_docservice_url"),
        username=settings.get("docservice_username"),
        password=settings.get("docservice_password"),
        upload_url=settings.get("docservice_upload_url"),
        service_key=signer,
        keyring=keyring,
    )

    # initialize all dynamic parts of application
    all_parts = project_info["app"]["parts"]
    restricted_parts = settings.get("parts") and [plugin.strip() for plugin in settings["parts"].split(",")]
    for part_name, part_path in all_parts.items():
        if not restricted_parts or part_name in restricted_parts:
            init = load_callable(part_path)
            init(sub_app, settings)

    sub_app.on_startup.append(mongodb.create_indexes)

    # add pyramid routes
    wsgi_handler = WSGIHandler(
        pyramid_main(
            global_config,
            **settings,
        )
    )
    sub_app.router.add_route("*", "/{path_info:.*}", wsgi_handler)
    return sub_app


def get_app(global_config, **settings):
    sub_app = get_sub_app(global_config, **settings)

    # === main app ===
    # Usually, if there is a version, there are multiple versions. Not our case 🤌
    app = web.Application()
    app.add_subapp(MAIN_ROUTE_PREFIX, sub_app)
    return app
