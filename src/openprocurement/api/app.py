# pylint: disable=wrong-import-position
import os
import sys

if not any(
    [
        "test" in sys.argv[0],
        "setup.py" in sys.argv[0],
        "PYTEST_XDIST_WORKER" in os.environ,
        "NO_GEVENT_MONKEY_PATCH" in os.environ,
    ]
):
    import gevent.monkey

    gevent.monkey.patch_all()

import configparser
import tomllib
from importlib import import_module
from logging import getLogger
from pathlib import Path

import sentry_sdk
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey
from paste.deploy.config import make_prefix_middleware
from pyramid.authorization import ACLAuthorizationPolicy as AuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPPreconditionFailed
from pyramid.renderers import JSON, JSONP
from pyramid.settings import asbool
from request_id_middleware.middleware import RequestIdMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.pyramid import PyramidIntegration

from openprocurement.api.auth import (
    AuthenticationPolicy,
    authenticated_role,
    check_accreditations,
)
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.database import MongodbStore
from openprocurement.api.translogger import make_filter as make_trans_logger_filter
from openprocurement.api.utils import (
    forbidden,
    get_currency_rates,
    json_dumps,
    precondition,
    request_params,
)

LOGGER = getLogger("{}.init".format(__name__))


logger = getLogger(__name__)


def load_config(filename):
    config = configparser.ConfigParser(interpolation=None)
    config.read(filename)
    config_dict = {section: dict(config[section]) for section in config.sections()}
    return config_dict


def load_pyproject():
    pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)
    return pyproject


def load_callable(path):
    module, func = path.split(":")
    return getattr(import_module(module), func)


def main(global_config, **settings):
    dsn = settings.get("sentry.dsn", None)
    if dsn:
        LOGGER.info("Init sentry sdk for {}".format(dsn))
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                LoggingIntegration(level=None, event_level=None),
                PyramidIntegration(),
            ],
            send_default_pii=True,
            max_request_body_size="always",
            environment=settings.get("sentry.environment", None),
            debug=settings.get("sentry.debug", False),
        )

    config = Configurator(
        autocommit=True,
        settings=settings,
        authentication_policy=AuthenticationPolicy(settings["auth.file"], __name__),
        authorization_policy=AuthorizationPolicy(),
        route_prefix=ROUTE_PREFIX,
    )
    config.include("pyramid_exclog")
    config.include("cornice")
    config.add_forbidden_view(forbidden)
    config.add_view(precondition, context=HTTPPreconditionFailed)
    config.add_request_method(request_params, "params", reify=True)
    config.add_request_method(authenticated_role, reify=True)
    config.add_request_method(check_accreditations)
    config.add_request_method(get_currency_rates, name="currency_rates", reify=True)
    config.add_renderer("json", JSON(serializer=json_dumps))
    config.add_renderer("prettyjson", JSON(indent=4, serializer=json_dumps))
    config.add_renderer("jsonp", JSONP(param_name="opt_jsonp", serializer=json_dumps))
    config.add_renderer("prettyjsonp", JSONP(indent=4, param_name="opt_jsonp", serializer=json_dumps))

    # mongodb
    config.registry.mongodb = MongodbStore(settings)

    # search for plugins
    pyproject = load_pyproject()
    all_modules = pyproject["tool"]["openprocurement"]["modules"]
    restricted_modules = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for module_name, module_path in all_modules.items():
        if not restricted_modules or module_name in restricted_modules:
            plugin = load_callable(module_path)
            plugin(config)

    # Document Service key
    config.registry.docservice_url = settings.get("docservice_url")
    config.registry.docservice_username = settings.get("docservice_username")
    config.registry.docservice_password = settings.get("docservice_password")
    config.registry.docservice_upload_url = settings.get("docservice_upload_url")

    # Catalog API host
    config.registry.catalog_api_host = settings.get("catalog_api_host")

    # Render API host
    config.registry.render_api_host = settings.get("render_api_host")
    config.registry.render_api_username = settings.get("render_api_username")
    config.registry.render_api_password = settings.get("render_api_password")

    # Sign API host
    config.registry.sign_api_host = settings.get("sign_api_host")
    config.registry.sign_api_username = settings.get("sign_api_username")
    config.registry.sign_api_password = settings.get("sign_api_password")

    # deprecated doc service url (for switching to the new host)
    # you can upload documents from it, then urls will be changed to registry.docservice_url
    # so they both must be the same document service
    config.registry.dep_docservice_url = settings.get("dep_docservice_url")

    signing_key = settings.get("dockey", "")
    signer = SigningKey(signing_key, encoder=HexEncoder) if signing_key else SigningKey.generate()
    config.registry.docservice_key = signer
    verifier = signer.verify_key

    config.registry.keyring = {verifier.encode(encoder=HexEncoder)[:8].decode(): verifier}
    dockeys = settings.get("dockeys", "")
    for key in dockeys.split("\0"):
        if key:
            config.registry.keyring[key[:8]] = VerifyKey(key, encoder=HexEncoder)

    config.registry.server_id = settings.get("id", "")

    config.registry.health_threshold = float(settings.get("health_threshold", 512))
    config.registry.health_threshold_func = settings.get("health_threshold_func", "all")
    config.registry.update_after = asbool(settings.get("update_after", True))

    config.add_tween("openprocurement.api.middlewares.DBSessionCookieMiddleware")
    app = config.make_wsgi_app()

    # We plan to move from PasteDeploy and pyramid.
    # At this stage we're going to move filters/middlewares from .ini file to the python code.
    # We still use .ini file to hold the configuration, until we ready to switch completely.
    # By default, we get only [app:api] block, so we need to load the entire config again.
    global_settings = load_config(global_config["__file__"])

    # transaction logger
    # we can drop "filter:translogger" config now, should work fine
    trans_logger_settings = global_settings.get("filter:translogger") or {}
    trans_logger_settings.pop("use", None)  # we already imported it 😉
    app = make_trans_logger_filter(
        global_config,
        logger_name=trans_logger_settings.get("logger_name", "wsgi"),
        set_logger_level=trans_logger_settings.get("set_logger_level", "WARNING"),
        setup_console_handler=trans_logger_settings.get("setup_console_handler", False),
    )(app)

    # request_id
    # does `req.environ[self.env_request_id] = req.headers[self.resp_header_client_request_id]`
    # we can drop "filter:request_id" config now, should work fine
    request_id_settings = global_settings.get("filter:request_id") or {}
    request_id_settings.pop("paste.filter_factory", None)
    app = RequestIdMiddleware.factory(
        global_config,
        env_request_id=request_id_settings.get("env_request_id", "REQUEST_ID"),
        resp_header_request_id=request_id_settings.get("resp_header_request_id", "X-Request-ID"),
    )(app)

    # prefix middleware
    # config is empty, means it doesn't really do with prefix.
    # translate_forwarded_server=True is default parameter means it translates HTTP_X_FORWARDED_ headers.
    # See source of paste.deploy.config.PrefixMiddleware for more details
    app = make_prefix_middleware(app, global_config)
    return app
