def is_test():
    import sys
    import os
    return any([
        "test" in sys.argv[0],
        "setup.py" in sys.argv[0],
        "PYTEST_XDIST_WORKER" in os.environ,
    ])


if not is_test():
    import gevent.monkey
    gevent.monkey.patch_all()

import os
import simplejson
import sentry_sdk
from datetime import datetime
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey
from logging import getLogger
from openprocurement.api.auth import AuthenticationPolicy, authenticated_role, check_accreditations
from openprocurement.api.database import MongodbStore
from openprocurement.api.utils import forbidden, request_params, precondition, get_currency_rates
from openprocurement.api.constants import ROUTE_PREFIX, TZ
from pkg_resources import iter_entry_points
from pyramid.authorization import ACLAuthorizationPolicy as AuthorizationPolicy
from pyramid.config import Configurator
from pyramid.renderers import JSON, JSONP
from pyramid.settings import asbool
from pyramid.httpexceptions import HTTPPreconditionFailed
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.pyramid import PyramidIntegration
from pytz import utc


LOGGER = getLogger("{}.init".format(__name__))


class CustomJSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            if not obj.tzinfo:
                obj = utc.localize(obj).astimezone(TZ)
            return obj.isoformat()
        return super().default(self, obj)


def json_dumps(data, **kw):
    kw["cls"] = CustomJSONEncoder
    del kw["default"]  # ignore pyramids default function provided, to use CustomJSONEncoder.default
    return simplejson.dumps(data, **kw)


def main(global_config, **settings):
    dsn = settings.get("sentry.dsn", None)
    if dsn:
        LOGGER.info("Init sentry sdk for {}".format(dsn))
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                LoggingIntegration(level=None, event_level=None),
                PyramidIntegration()],
            send_default_pii=True,
            request_bodies="always",
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

    # search for plugins
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.api.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)

    # mongodb
    config.registry.mongodb = MongodbStore(settings)

    # Document Service key
    config.registry.docservice_url = settings.get("docservice_url")
    config.registry.docservice_username = settings.get("docservice_username")
    config.registry.docservice_password = settings.get("docservice_password")
    config.registry.docservice_upload_url = settings.get("docservice_upload_url")

    # deprecated doc service url (for switching to the new host)
    # you can upload documents from it, then urls will be changed to registry.docservice_url
    # so they both must be the same document service
    config.registry.dep_docservice_url = settings.get("dep_docservice_url")

    signing_key = settings.get('dockey', '')
    signer = SigningKey(signing_key, encoder=HexEncoder) if signing_key else SigningKey.generate()
    config.registry.docservice_key = signer
    verifier = signer.verify_key

    config.registry.keyring = {
        verifier.encode(encoder=HexEncoder)[:8].decode(): verifier
    }
    dockeys = settings.get('dockeys', '')
    for key in dockeys.split('\0'):
        if key:
            config.registry.keyring[key[:8]] = VerifyKey(key, encoder=HexEncoder)

    config.registry.server_id = settings.get("id", "")

    # search subscribers
    subscribers_keys = [k for k in settings if k.startswith("subscribers.")]
    for k in subscribers_keys:
        subscribers = settings[k].split(",")
        for subscriber in subscribers:
            for entry_point in iter_entry_points("openprocurement.{}".format(k), subscriber):
                if entry_point:
                    plugin = entry_point.load()
                    plugin(config)

    config.registry.health_threshold = float(settings.get("health_threshold", 512))
    config.registry.health_threshold_func = settings.get("health_threshold_func", "all")
    config.registry.update_after = asbool(settings.get("update_after", True))

    config.add_tween("openprocurement.api.middlewares.DBSessionCookieMiddleware")
    app = config.make_wsgi_app()
    return app
