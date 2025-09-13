import os

from aiohttp import web
from aiohttp_wsgi import WSGIHandler

os.environ["NO_GEVENT_MONKEY_PATCH"] = "🚫🐒🚫🐒🚫🐒🚫🐒🚫🐒🚫🐒🚫"


# === aiohttp app ===
async def ping(request):
    return web.json_response({"msg": "pong"})


def get_app(global_config, **settings):
    # pylint: disable=import-outside-toplevel
    from openprocurement.api.app import main as pyramid_main

    # add aiohttp routes
    app = web.Application()
    app.router.add_route("GET", "/ping/", ping)

    # add pyramid routes
    wsgi_handler = WSGIHandler(pyramid_main(global_config, **settings))
    app.router.add_route("*", "/{path_info:.*}", wsgi_handler)
    return app
