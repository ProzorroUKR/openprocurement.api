# -*- coding: utf-8 -*-
import unittest
from openprocurement.tender.openuadefense.tests import (
    auction,
    award,
    bid,
    cancellation,
    chronograph,
    complaint,
    contract,
    document,
    lot,
    question,
    tender
)


def suite():
    suite.addTest(auction.suite())
    suite.addTest(award.suite())
    suite.addTest(bid.suite())
    suite.addTest(cancellation.suite())
    suite.addTest(chronograph.suite())
    suite.addTest(complaint.suite())
    suite.addTest(contract.suite())
    suite.addTest(document.suite())
    suite.addTest(lot.suite())
    suite.addTest(question.suite())
    suite.addTest(tender.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
