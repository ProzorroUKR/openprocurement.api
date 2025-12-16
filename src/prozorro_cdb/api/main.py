# pylint: disable=wrong-import-position
import os

os.environ["NO_GEVENT_MONKEY_PATCH"] = "🚫🐒🚫🐒🚫🐒🚫🐒🚫🐒🚫🐒🚫"

from aiohttp import web
from aiohttp_pydantic import oas
from aiohttp_wsgi import WSGIHandler
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey

from openprocurement.api.app import load_callable, load_config, load_pyproject
from openprocurement.api.constants import ROUTE_PREFIX
from prozorro_cdb.api.auth import get_login_middleware
from prozorro_cdb.api.database.store import MongodbStore
from prozorro_cdb.api.handlers.base import ping
from prozorro_cdb.api.middlewares import (
    access_logger_middleware,
    context_middleware,
    convert_response_to_json,
    db_session_middleware,
    error_middleware,
    jsonp_and_pretty_middleware,
)
from prozorro_cdb.api.settings import DocStorageConfig


def get_aiohttp_sub_app(global_config, **settings):
    # init app
    sub_app = web.Application()
    sub_app["project_info"] = project_info = load_pyproject()  # load info from pyproject.toml

    # load settings
    global_settings = load_config(global_config["__file__"])
    trans_logger_settings = global_settings.get("filter:translogger") or {}
    trans_logger_disabled = trans_logger_settings.get("set_logger_level", "WARNING") == "WARNING"

    # middlewares
    if not trans_logger_disabled:
        sub_app.middlewares.append(access_logger_middleware)  # should be the first and the last to better track time

    auth_file = settings["auth.file"].replace("%(here)s", global_config["here"])
    sub_app.middlewares.extend(
        [
            jsonp_and_pretty_middleware,  # last when we return response
            get_login_middleware(auth_file),  # should be before context_middleware
            context_middleware,
            db_session_middleware,
            error_middleware,
            convert_response_to_json,
        ]
    )

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
    all_parts = project_info["tool"]["prozorro_cdb"]["parts"]
    restricted_parts = settings.get("parts") and [plugin.strip() for plugin in settings["parts"].split(",")]
    for part_name, part_path in all_parts.items():
        if not restricted_parts or part_name in restricted_parts:
            init = load_callable(part_path)
            init(sub_app, settings)

    sub_app.on_startup.append(mongodb.create_indexes)

    return sub_app


def get_pyramid_sub_app(global_config, **settings):
    # pylint: disable=import-outside-toplevel
    from openprocurement.api.app import main as pyramid_main

    pyramid_handler = WSGIHandler(
        pyramid_main(
            global_config,
            **settings,
        )
    )

    sub_app = web.Application()
    sub_app.router.add_route("*", "/{path_info:.*}", pyramid_handler)

    return sub_app


def pyramid_first_middleware(pyramid_sub_app):
    @web.middleware
    async def middleware(request, handler):
        """Middleware that tries pyramid app first then falls back to aiohttp handler"""

        # QUICK FIX: Skip Pyramid for /violation_reports paths, handle with aiohttp first
        # TODO: Remove this once we have a proper solution for handling routes
        if "/violation_reports" in request.path:
            return await handler(request)

        # Try pyramid first
        response = await pyramid_sub_app._handle(request.clone())
        if response.headers.get("X-Pyramid-Route-Not-Matched") != "true":
            return response

        # No route matched in pyramid, let aiohttp handler try
        return await handler(request)

    return middleware


def get_app(global_config, **settings):
    app = web.Application()

    # add pyramid sub-app (via middleware)
    pyramid_sub_app = get_pyramid_sub_app(global_config, **settings)
    app.middlewares.append(pyramid_first_middleware(pyramid_sub_app))

    # add aiohttp sub-app
    aiohttp_sub_app = get_aiohttp_sub_app(global_config, **settings)
    app.add_subapp(ROUTE_PREFIX, aiohttp_sub_app)

    return app
