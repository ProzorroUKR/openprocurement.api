from cornice.service import Service
from pyramid.response import Response
from openprocurement.tender.core.render import render_tender_txt

tender_render_service = Service(name="render_tender", path="/render/txt/tenders/{tender_id}")


@tender_render_service.get()
def get_tender(request):
    data = request.tender_doc
    text = render_tender_txt(data)
    return Response(text=text)
