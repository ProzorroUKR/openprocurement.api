from locust import HttpUser, task, constant
from collections import deque
from data import tender, bid, USERS
from time import sleep
import random


TENDERS_URL = "/api/2.5/tenders"
TENDER_URL = None
DS_URL = "http://ds.k8s.prozorro.gov.ua/upload"


# test process data
BIDS = deque(maxlen=200)


class User(HttpUser):
    wait_time = constant(0)

    def __init__(self, *args, **kwargs):
        global TENDER_URL

        super().__init__(*args, **kwargs)
        self.client.auth = USERS["broker"]

        if TENDER_URL is None:
            # get cookies
            self.client.get(TENDERS_URL)

            # post tender
            result = self.client.post(TENDERS_URL, json=tender)
            assert result.status_code == 201, result.content
            result_json = result.json()
            tender_data = result_json["data"]
            tender_id = tender_data["id"]
            # self.tender_token = result_json["access"]["token"]
            TENDER_URL = f"{TENDERS_URL}/{tender_id}"

            # upload a file
            self.client.auth = USERS["ds"]
            result = self.client.post(DS_URL, files={'file': ('test.jpeg', b"data", 'image/jpeg')})
            assert result.status_code == 200, result.content
            document = result.json()["data"]
            bid["documents"] = [document] * 20
            print("Doc uploaded", document)

            print(f"waiting for the bidding stage of {TENDER_URL}")
            sleep(20)  # "enquiryPeriod": { "endDate": (now + timedelta(seconds=20)).isoformat()
            self.client.auth = USERS["chronograph"]
            result = self.client.patch(TENDER_URL, json={"data": {}})
            assert result.status_code == 200, result.content
            assert result.json()["data"]["status"] == "active.tendering"

            self.client.auth = USERS["broker"]
        # else:
        #     # wait tender is ready
        #     tender_data = {"status": "active.enquiries"}
        #     while tender_data["status"] == "active.enquiries":
        #         r = self.client.get(TENDER_URL)
        #         tender_data = r.json()["data"]
        #         print(f"waiting bidding status: {tender_data['status']}")
        #         sleep(5)

    @task(20)
    def post_bid(self):
        result = self.client.post(
            f"{TENDER_URL}/bids",
            name="/api/tenders/{uuid}/bid",
            json=bid
        )
        if result.status_code != 201:
            print(result.content)
        else:
            response = result.json()
            BIDS.append(
                (response["data"]["id"], response["access"]["token"])
            )

    @task(10)
    def get_bid(self):
        try:
            uid, token = random.choice(BIDS)
        except IndexError:  # if empty
            return

        response = self.client.get(
            f"{TENDER_URL}/bids/{uid}?acc_token={token}",
            name="/api/tenders/{uuid}/bid/{uuid}",
        )
        if response.status_code not in (404, 200):
            print(response.json())

    @task(20)
    def edit_bid(self):
        try:
            uid, token = BIDS.pop()
        except IndexError:  # if empty
            return

        response = self.client.patch(
            f"{TENDER_URL}/bids/{uid}?acc_token={token}",
            name="/api/tenders/{uuid}/bid/{uuid}",
            json={"data": {"value": {"amount": random.randint(100, 499)}}}
        )
        if response.status_code != 200:
            print(response.json())

        BIDS.append(
            (uid, token)
        )

    @task
    def delete_bid(self):
        try:
            uid, token = BIDS.pop()
        except IndexError:  # if empty
            return

        response = self.client.patch(
            f"{TENDER_URL}/bids/{uid}?acc_token={token}",
            name="/api/tenders/{uuid}/bid/{uuid}",
            json={"data": {"value": {"amount": random.randint(100, 499)}}}
        )
        if response.status_code != 200:
            print(response.json())

        BIDS.append(
            (uid, token)
        )

    @task(20)
    def post_bid_document(self):
        try:
            uid, token = BIDS.pop()
        except IndexError:  # if empty
            return

        response = self.client.post(
            f"{TENDER_URL}/bids/{uid}/documents?acc_token={token}",
            name="/api/tenders/{uuid}/bid/{uuid}/documents",
            json={"data": bid["documents"]}
        )
        if response.status_code != 201:
            print(response.json())

        BIDS.append(
            (uid, token)
        )
