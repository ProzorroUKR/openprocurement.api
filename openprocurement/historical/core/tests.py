from openprocurement.api.tests.base import BaseWebTest, test_tender_data
from openprocurement.historical import HEADER


class HistoricalTest(BaseWebTest):

    def test_extract_header(self):
        r = self.app.post_json('/tenders', {'data': test_tender_data}).json['data']
    
        _get = self.app.get
        _path = '/tenders/{}'.format(r['id']),

        response = _get(_path, headers=dict(HEADER, 1))
        self.assertEqual(self.app.request.extract_header(), 1)
        
        for header in [1.1, -1, -1.5, "", "asd"]:
            response = _get(_path, headers=dict(HEADER, header))
            self.assertFalse(self.app.request.extract_header())
