# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
    TenderDocumentWithDSResourceTestMixin,
)


class TenderDocumentResourceTest(BaseTenderUAContentWebTest, TenderDocumentResourceTestMixin):
    docservice = False


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
