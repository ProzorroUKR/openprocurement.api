from locust import HttpUser, task, constant
from collections import deque
from data import plan, USERS
import random


PLANS_URL = "/api/2.5/plans"

# test process data
CREATED_PLANS = deque(maxlen=200)
PLANS = deque(maxlen=10000)


class User(HttpUser):
    wait_time = constant(0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.auth = USERS["broker"]

    def list(self, descending: str = "", limit: int = 100, opt_fields: str = ""):
        query = f"?descending={descending}&limit={limit}&opt_fields={opt_fields}"
        url = f"{PLANS_URL}{query}"
        while True:
            result = self.client.get(
                url,
                name=f"/api/plans{query}",
            )
            if result.status_code == 200:
                resp = result.json()
                if not resp["data"]:
                    break
                else:
                    for e in resp["data"]:
                        PLANS.append(e["id"])
                    url = resp["next_page"]["path"]
            else:
                print(result.content)

    @task(1)
    def list_forward(self):
        self.list()

    @task(1)
    def list_backward(self):
        self.list(descending="1")

    # @task(1)
    # def list_forward_max_limit(self):
    #     self.list(limit=1000)
    #
    # @task(1)
    # def list_backward_max_limit(self):
    #     self.list(descending="1", limit=1000)

    # "dateCreated", "planID", "dateModified"
    @task(1)
    def list_forward_opt_field(self):
        self.list(opt_fields="dateCreated,planID")

    @task(1)
    def list_backward_opt_field(self):
        self.list(descending="1", opt_fields="dateCreated,planID")

    @task(80000)
    def get_plan(self):
        try:
            uid = random.choice(PLANS)
        except IndexError:  # if empty
            return

        response = self.client.get(
            f"{PLANS_URL}/{uid}",
            name="/api/plans/{uuid}",
        )
        if response.status_code not in (404, 200):
            print(response.content)

    # @task(10)
    # def post_plan(self):
    #     result = self.client.post(
    #         PLANS_URL,
    #         name="/api/plans",
    #         json={"data": plan}
    #     )
    #     if result.status_code != 201:
    #         print(result.content)
    #     else:
    #         response = result.json()
    #         CREATED_PLANS.append(
    #             (response["data"]["id"],
    #              response["access"]["token"])
    #         )

    # @task(10)
    # def edit_plan(self):
    #     try:
    #         uid, token = CREATED_PLANS.pop()
    #     except IndexError:  # if empty
    #         return
    #
    #     response = self.client.patch(
    #         f"{PLANS_URL}/{uid}?acc_token={token}",
    #         name="/api/plans/{uuid}",
    #         json={"data": {"status": "scheduled"}}
    #     )
    #     if response.status_code != 200:
    #         print(response.json())


