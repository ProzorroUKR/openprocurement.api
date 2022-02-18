# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentWithDSResourceTestMixin,
)

from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest


class TenderDocumentWithDSResourceTest(BaseTenderContentWebTest, TenderDocumentWithDSResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
