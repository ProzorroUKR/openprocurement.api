from os.path import dirname, join
import configparser
from cornice.service import Service
from pyramid.response import Response

constants = Service(name="constants", path="/constants", renderer="json")


@constants.get()
def get_constants(request):
    file_path = join(dirname(dirname(__file__))) + '/constants.ini'
    config = configparser.ConfigParser()
    config.read(file_path)
    result = {k.upper(): v for k, v in config["DEFAULT"].items()}
    return Response(json_body=result)
