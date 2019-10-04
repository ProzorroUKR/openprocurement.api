# -*- coding: utf-8 -*-


# TenderSwitchAuctionResourceTest
def switch_to_auction(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


# TenderLotSwitch1BidResourceTest
def switch_to_qualification(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
