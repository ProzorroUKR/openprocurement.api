from os.path import dirname, join
import configparser
from cornice.service import Service
from pyramid.response import Response
from openprocurement.api.constants import CONSTANTS_FILE_PATH

constants = Service(name="constants", path="/constants", renderer="json")


@constants.get()
def get_constants(request):
    config = configparser.ConfigParser()
    config.read(CONSTANTS_FILE_PATH)
    result = {k.upper(): v for k, v in config["DEFAULT"].items()}
    return Response(json_body=result)
