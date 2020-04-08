# -*- coding: utf-8 -*-

# TenderSwitchQualificationResourceTest
def switch_to_qualification(self):
    self.set_status("active.qualification", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 1)


# TenderSwitchUnsuccessfulResourceTest

def switch_to_unsuccessful(self):
    self.set_status("active.qualification", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual(set([i["status"] for i in response.json["data"]["lots"]]), set(["unsuccessful"]))
