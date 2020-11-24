import unittest
from mock import MagicMock, patch
from hashlib import sha512

from openprocurement.tender.core.views.tender_credentials import TenderResource


class TestTenderCredentials(unittest.TestCase):
    class Tender(object):
        def __init__(self):
            self.store = dict()

        def __setitem__(self, key, value):
            self.store[key] = value

        def __getitem__(self, key):
            return self.store[key]

    def test_tender_credentials(self):
        request = MagicMock()
        context = MagicMock()
        tender = self.Tender()
        tender.serialize = MagicMock(return_value=tender)
        tender.owner_token = ""
        request.validated = {"tender": tender}
        response = TenderResource(request, context).get()

        self.assertEqual(sha512(tender.owner_token.encode("utf-8")).hexdigest(), response["data"]["tender_token"])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTenderCredentials))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
