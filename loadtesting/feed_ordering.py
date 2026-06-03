"""
Load test: feed ordering anomaly detection
==========================================

Reproduces and detects the race condition where tenders appear in the DB
with a `public_modified` value lower than an already-served feed offset,
causing them to be permanently skipped by crawlers.

The root cause: MongoDB's $$NOW captures wall-clock time at the START of an
operation, not at commit time. Concurrent writes can commit out of $$NOW order,
inserting items "behind" an offset a crawler already passed.

User classes
------------
- TenderUpdaterSmall   — creates small tenders (1 item) and patches them at max rate
- TenderUpdaterLarge   — creates large tenders (10 items) and patches them at max rate
- FeedOrderingDetector — polls the feed and logs anomalies to feed_anomalies.txt

Recommended run (adjust -u to control concurrency):
    locust -f feed_ordering.py --host http://localhost:8000

With e.g. -u 21:
    - 1x  FeedOrderingDetector
    - 10x TenderUpdaterSmall
    - 10x TenderUpdaterLarge
"""

import random
import threading
from datetime import datetime, timedelta
from time import sleep, time

from data import USERS
from locust import HttpUser, constant, task

TENDERS_URL = "/api/2.5/tenders"
DS_URL = "http://ds.k8s.prozorro.gov.ua/upload"

REPORT_FILE = "/mnt/locust/feed_anomalies.txt"
_report_lock = threading.Lock()

# How many tenders each updater user creates on startup.
# More tenders = more concurrent patch targets = higher collision probability.
TENDERS_PER_USER = 10

# How long the detector waits between snapshot_1 and the re-fetch.
# Should be long enough for some late commits to appear, but short enough
# that the feed hasn't moved too far ahead.
DETECTOR_WAIT_SEC = 3

now = datetime.utcnow()


# ---------------------------------------------------------------------------
# Tender fixtures
# ---------------------------------------------------------------------------

_PROCURING_ENTITY = {
    "name": "Державне управління справами",
    "identifier": {
        "scheme": "UA-EDR",
        "id": "00037256",
        "uri": "http://www.dus.gov.ua/",
        "legalName": "Державне управління справами",
    },
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {"name": "Державне управління справами", "telephone": "+380957777777"},
    "kind": "general",
    "signerInfo": {
        "name": "Test Testovich",
        "telephone": "+380950000000",
        "email": "example@email.com",
        "iban": "1" * 15,
        "authorizedBy": "Статут компанії",
        "position": "Генеральний директор",
    },
}

LOT_ID = "a" * 32  # fixed lot id used in fixtures

_ITEM_TEMPLATE = {
    "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
    "additionalClassifications": [
        {"scheme": "ДКПП", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ],
    "unit": {"name": "item", "code": "KGM"},
    "quantity": 5,
    "relatedLot": LOT_ID,
    "deliveryDate": {
        "startDate": now.isoformat(),
        "endDate": (now + timedelta(days=300)).isoformat(),
    },
    "deliveryAddress": {
        "countryName": "Україна",
        "postalCode": "79000",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова 1",
    },
}

_MILESTONES_BASE = [
    {
        "title": "signingTheContract",
        "type": "delivery",
        "duration": {"days": 2, "type": "calendar"},
        "sequenceNumber": 1,
        "code": "standard",
        "percentage": 100,
    }
]


def _make_tender(items, milestones):
    return {
        "data": {
            "mode": "test",
            "title": "Тендер для тестування порядку фіду",
            "contractTemplateName": "00000000.0002.01",
            "mainProcurementCategory": "goods",
            "procuringEntity": _PROCURING_ENTITY,
            "value": {"amount": 500, "currency": "UAH"},
            "lots": [
                {
                    "id": LOT_ID,
                    "title": "Лот 1",
                    "value": {"amount": 500, "currency": "UAH"},
                    "minimalStep": {"amount": 15, "currency": "UAH"},
                }
            ],
            "items": items,
            "enquiryPeriod": {
                "startDate": (now + timedelta(days=7)).isoformat(),
                "endDate": (now + timedelta(days=27)).isoformat(),
            },
            "tenderPeriod": {"endDate": (now + timedelta(days=300)).isoformat()},
            "procurementMethodType": "belowThreshold",
            "milestones": milestones,
        },
        "config": {
            "awardComplainDuration": 2,
            "cancellationComplainDuration": 0,
            "clarificationUntilDuration": 1,
            "enquiryPeriodRegulation": 0,
            "hasAuction": True,
            "hasAwardComplaints": False,
            "hasAwardingOrder": True,
            "hasCancellationComplaints": False,
            "hasEnquiries": True,
            "hasPreSelectionAgreement": False,
            "hasPrequalification": False,
            "hasQualificationComplaints": False,
            "hasTenderComplaints": False,
            "hasValueEstimation": True,
            "hasValueRestriction": True,
            "minBidsNumber": 1,
            "minEnquiriesDuration": 3,
            "minTenderingDuration": 2,
            "qualificationComplainDuration": 0,
            "qualificationDuration": 0,
            "restricted": False,
            "tenderComplainRegulation": 0,
            "valueCurrencyEquality": True,
        },
    }


# Small: 1 item, 2 milestones — minimal document size
TENDER_SMALL = _make_tender(
    items=[{**_ITEM_TEMPLATE, "description": "Малий товар"}],
    milestones=_MILESTONES_BASE
    + [
        {
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 900, "type": "calendar"},
            "sequenceNumber": 2,
            "percentage": 100,
        },
    ],
)

# Large: 10 items with long descriptions, 5 milestones — larger document,
# more data written per update → longer write time → higher chance of
# concurrent commits landing out of $$NOW order
TENDER_LARGE = _make_tender(
    items=[
        {
            **_ITEM_TEMPLATE,
            "description": f"Товар {i}: " + ("Опис товару для збільшення розміру документа. " * 10),
            "quantity": i * 7,
        }
        for i in range(1, 11)
    ],
    milestones=_MILESTONES_BASE
    + [
        {
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 5 * i, "type": "calendar"},
            "sequenceNumber": len(_MILESTONES_BASE) + i,
            "percentage": 5,
        }
        for i in range(1, 21)
    ],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _upload_notice_doc(client, tender_id, token):
    """
    Upload a fake .p7s file to the document service and attach it to the tender
    as a 'notice' document. Required before activating (draft → active.enquiries).

    The document title must end with '.p7s' and documentType must be 'notice'.
    """
    prev_auth = client.auth
    client.auth = USERS["ds"]
    ds_resp = client.post(
        DS_URL,
        name="POST DS [notice .p7s]",
        files={"file": ("sign.p7s", b"0" * 32, "application/pkcs7-signature")},
    )
    client.auth = prev_auth

    if ds_resp.status_code != 200:
        print(f"DS upload failed: {ds_resp.status_code} {ds_resp.text}")
        return False

    doc = ds_resp.json()["data"]
    post_resp = client.post(
        f"{TENDERS_URL}/{tender_id}/documents?acc_token={token}",
        name="POST /tenders/{id}/documents [notice]",
        json={
            "data": {
                "title": "sign.p7s",
                "url": doc["url"],
                "hash": doc["hash"],
                "format": "application/pkcs7-signature",
                "documentType": "notice",
            }
        },
    )
    if post_resp.status_code != 201:
        print(f"Notice doc POST failed: {post_resp.json()}")
        return False
    return True


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------


def _write_report(snapshot_1, late_arrivals, pm_min, pm_max):
    """Append a human-readable anomaly entry to REPORT_FILE."""
    lines = [
        "=" * 70,
        f"ANOMALY DETECTED  {datetime.utcnow().isoformat()}",
        f"Feed window:  public_modified [{pm_min:.6f} … {pm_max:.6f}]",
        f"Late arrivals in window: {len(late_arrivals)}",
        "",
        "SNAPSHOT 1 (was):",
    ]
    for item in snapshot_1:
        lines.append(f"  {item['public_modified']:.6f}  {item['id']}")

    lines += ["", "LATE ARRIVALS (з'явились після але з public_modified всередині вікна):"]
    for item in late_arrivals:
        marker = ">>>"
        lines.append(f"  {marker} {item['public_modified']:.6f}  {item['id']}")

    lines += ["", "DIFF (що змінилось):"]
    ids_1 = {i["id"] for i in snapshot_1}
    merged = sorted(
        list(snapshot_1) + late_arrivals,
        key=lambda x: x["public_modified"],
    )
    for item in merged:
        tag = "  NEW" if item["id"] not in ids_1 else "     "
        lines.append(f"  {tag}  {item['public_modified']:.6f}  {item['id']}")

    lines.append("=" * 70 + "\n")

    with _report_lock:
        with open(REPORT_FILE, "a") as f:
            f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Locust user classes
# ---------------------------------------------------------------------------


class TenderUpdaterSmall(HttpUser):
    """
    Створює TENDERS_PER_USER малих тендерів при старті,
    потім безперервно патчить їх, генеруючи паралельні записи в MongoDB.

    Малий тендер = малий документ = відносно швидкий запис.
    Використовуйте багато інстансів для максимальної конкуренції.
    """

    wait_time = constant(0)

    def on_start(self):
        self.client.auth = USERS["broker"]
        self._pool = []  # list of (tender_id, access_token)

        for _ in range(TENDERS_PER_USER):
            resp = self.client.post(
                TENDERS_URL,
                json=TENDER_SMALL,
                name="POST /tenders [small setup]",
            )
            if resp.status_code != 201:
                print(f"POST failed: {resp.json()}")
                continue
            body = resp.json()
            tid = body["data"]["id"]
            token = body["access"]["token"]
            # Activation requires a notice document (.p7s) uploaded to DS first.
            if not _upload_notice_doc(self.client, tid, token):
                continue
            # Tenders start in "draft" (is_public=False, invisible in feed).
            # Patch to "active.enquiries" to make them visible.
            activate = self.client.patch(
                f"{TENDERS_URL}/{tid}?acc_token={token}",
                json={"data": {"status": "active.enquiries"}},
                name="PATCH /tenders/{id} [small activate]",
            )
            if activate.status_code == 200:
                self._pool.append((tid, token))
            else:
                print(f"Activate failed: {activate.json()}")

    @task
    def patch_tender(self):
        if not self._pool:
            return
        tid, token = random.choice(self._pool)
        # Patch title — editable in active.enquiries, no complex validation.
        # The full document is replaced in MongoDB each time, so even a small
        # PATCH payload exercises a full document write of the stored object.
        new_title = f"Тендер (small) оновлено {random.randint(1, 9999)}"
        self.client.patch(
            f"{TENDERS_URL}/{tid}?acc_token={token}",
            name="PATCH /tenders/{id} [small]",
            json={"data": {"title": new_title}},
        )


class TenderUpdaterLarge(HttpUser):
    """
    Те саме що TenderUpdaterSmall, але для великих тендерів.

    Великий тендер = великий документ = повільніший запис = вища ймовірність
    того що $$NOW буде захоплено раніше, а коміт відбудеться пізніше інших.
    Це найкраще відтворює race condition з public_modified.
    """

    wait_time = constant(0)

    def on_start(self):
        self.client.auth = USERS["broker"]
        self._pool = []

        for _ in range(TENDERS_PER_USER):
            resp = self.client.post(
                TENDERS_URL,
                json=TENDER_LARGE,
                name="POST /tenders [large setup]",
            )
            if resp.status_code != 201:
                print(f"POST failed: {resp.json()}")
                continue
            body = resp.json()
            tid = body["data"]["id"]
            token = body["access"]["token"]
            if not _upload_notice_doc(self.client, tid, token):
                continue
            activate = self.client.patch(
                f"{TENDERS_URL}/{tid}?acc_token={token}",
                json={"data": {"status": "active.enquiries"}},
                name="PATCH /tenders/{id} [large activate]",
            )
            if activate.status_code == 200:
                self._pool.append((tid, token))
            else:
                print(f"Activate failed: {activate.json()}")

    @task
    def patch_tender(self):
        if not self._pool:
            return
        tid, token = random.choice(self._pool)
        new_title = f"Тендер (large) оновлено {random.randint(1, 9999)}"
        self.client.patch(
            f"{TENDERS_URL}/{tid}?acc_token={token}",
            name="PATCH /tenders/{id} [large]",
            json={"data": {"title": new_title}},
        )


class FeedOrderingDetector(HttpUser):
    """
    Детектор аномалій порядку у фіді. Запускайте рівно 1 інстанс.

    Алгоритм (два запити):
    ──────────────────────
    1. GET /tenders?descending=1&limit=N&opt_fields=public_modified
       → snapshot_1: найсвіжіші N тендерів, відсортовані newest→oldest.
       Фіксуємо вікно [pm_min … pm_max].

    2. Чекаємо DETECTOR_WAIT_SEC секунд поки тривають паралельні оновлення.

    3. GET /tenders?offset=<pm_min - ε>&limit=2N&opt_fields=public_modified
       → snapshot_2: всі тендери з public_modified > pm_min - ε (форвардний фід).
       Повторне читання того самого вікна + те що з'явилось після.

    4. late_arrivals = тендери в snapshot_2, яких НЕ БУЛО в snapshot_1,
       але чий public_modified < pm_max (тобто вони всередині вікна, не в хвості).

       Такі тендери — це саме і є "late commits": вони отримали $$NOW раніше
       за pm_max, але закомітились пізніше ніж snapshot_1 був знятий.
       Реальний crawler з offset=pm_max їх би назавжди пропустив.

    5. Якщо є late_arrivals → пишемо в feed_anomalies.txt.
    """

    wait_time = constant(0)  # no idle time — loop as fast as possible
    SNAPSHOT_LIMIT = 200

    def on_start(self):
        self.client.auth = USERS["broker"]
        with _report_lock:
            with open(REPORT_FILE, "w") as f:
                f.write(
                    f"Feed ordering anomaly report\n" f"Started: {datetime.utcnow().isoformat()}\n" f"{'=' * 70}\n\n"
                )
        # Give updaters time to create their tenders before we start polling
        sleep(15)

    def _fire(self, start: float, name: str, exc: Exception | None = None):
        """Report a virtual request event so Locust tracks success/failure counts."""
        self.environment.events.request.fire(
            request_type="DETECT",
            name=name,
            response_time=(time() - start) * 1000,
            response_length=0,
            exception=exc,
            context={},
        )

    @task
    def detect(self):
        start = time()

        # ── Step 1: snapshot_1 ──────────────────────────────────────────────
        resp = self.client.get(
            f"{TENDERS_URL}?descending=1" f"&limit={self.SNAPSHOT_LIMIT}" f"&opt_fields=public_modified" f"&mode=test",
            name="GET /tenders [detector: snapshot_1]",
        )
        if resp.status_code != 200:
            self._fire(start, "feed ordering check", exc=Exception(f"snapshot_1 HTTP {resp.status_code}"))
            return
        snapshot_1 = resp.json().get("data", [])
        if len(snapshot_1) < 5:
            print("snapshot_1 too small (not enough data yet)")
            self._fire(start, "feed ordering check", exc=Exception("snapshot_1 too small (not enough data yet)"))
            return

        ids_1 = {item["id"] for item in snapshot_1}
        # descending → snapshot_1[0] = newest, snapshot_1[-1] = oldest
        pm_max = snapshot_1[0]["public_modified"]
        pm_min = snapshot_1[-1]["public_modified"]

        # ── Step 2: wait ────────────────────────────────────────────────────
        sleep(DETECTOR_WAIT_SEC)

        # ── Step 3: re-fetch same window (forward feed) ─────────────────────
        # We need items with public_modified >= pm_min (inclusive).
        #
        # The offset mechanism in views/base.py:
        #   skip_len > 0  →  inclusive_filter=True  →  DB uses $gte
        #   items at the boundary are skipped ONLY IF actual_skip_len == skip_len
        #                                          AND actual_skip_hash == skip_hash
        #
        # By passing a deliberately wrong skip_len (999) and skip_hash,
        # the hash check will always fail, so items at exactly pm_min
        # are included in the result.
        offset = f"{pm_min}.999.wronghash"
        resp2 = self.client.get(
            f"{TENDERS_URL}?limit={self.SNAPSHOT_LIMIT * 2}"
            f"&offset={offset}"
            f"&opt_fields=public_modified"
            f"&mode=test",
            name="GET /tenders [detector: re-fetch]",
        )
        if resp2.status_code != 200:
            print(f"re-fetch HTTP {resp2.status_code}")
            self._fire(start, "feed ordering check", exc=Exception(f"re-fetch HTTP {resp2.status_code}"))
            return
        snapshot_2 = resp2.json().get("data", [])

        # ── Step 4: find late arrivals ───────────────────────────────────────
        # Items that:
        #   - were NOT in snapshot_1 (new, appeared after)
        #   - have public_modified < pm_max (inside the original window, not at the tail)
        late_arrivals = [
            item for item in snapshot_2 if item["id"] not in ids_1 and item.get("public_modified", 0) < pm_max
        ]

        # ── Step 5: report ───────────────────────────────────────────────────
        if late_arrivals:
            exc = Exception(f"{len(late_arrivals)} late arrival(s) in window [{pm_min:.6f}…{pm_max:.6f}]")
            self._fire(start, "feed ordering check", exc=exc)
            print(f"[ANOMALY] {exc}")
            _write_report(snapshot_1, late_arrivals, pm_min, pm_max)
        else:
            self._fire(start, "feed ordering check")
            print(f"[OK] window [{pm_min:.6f} … {pm_max:.6f}], {len(snapshot_2)} items checked")
