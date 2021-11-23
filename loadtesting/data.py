from datetime import datetime, timedelta

USERS = dict(
    broker=("broker", ""),
    chronograph=("chronograph", ""),
    ds=("test", "test"),
)

accelerator = 14400
now = datetime.utcnow()
tender = {
  "data": {
    "mode": "test",
    "procurementMethodDetails": f"quick, accelerator={accelerator}",
    "title": "футляри до державних нагород",
    "mainProcurementCategory": "goods",
    "procuringEntity": {
      "name": "Державне управління справами",
      "identifier": {
        "scheme": "UA-EDR",
        "id": "00037256",
        "uri": "http://www.dus.gov.ua/",
        "legalName": "Державне управління справами"
      },
      "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1"
      },
      "contactPoint": {
        "name": "Державне управління справами",
        "telephone": "+380957777777"
      },
      "kind": "general"
    },
    "value": {
      "amount": 500,
      "currency": "UAH"
    },
    "minimalStep": {
      "amount": 15,
      "currency": "UAH"
    },
    "items": [
      {
        "description": "футляри до державних нагород",
        "classification": {
          "scheme": "ДК021",
          "id": "44617100-9",
          "description": "Cartons"
        },
        "additionalClassifications": [
          {
            "scheme": "ДКПП",
            "id": "17.21.1",
            "description": "папір і картон гофровані, паперова й картонна тара"
          }
        ],
        "unit": {
          "name": "item",
          "code": "44617100-9"
        },
        "quantity": 5,
        "deliveryDate": {
          "startDate": now.isoformat(),
          "endDate": (now + timedelta(days=300)).isoformat()
        },
        "deliveryAddress": {
          "countryName": "Україна",
          "postalCode": "79000",
          "region": "м. Київ",
          "locality": "м. Київ",
          "streetAddress": "вул. Банкова 1"
        }
      }
    ],
    "enquiryPeriod": {
      "startDate": now.isoformat(),
      "endDate": (now + timedelta(seconds=20)).isoformat()
    },
    "tenderPeriod": {
      "endDate": (now + timedelta(days=300)).isoformat()
    },
    "procurementMethodType": "belowThreshold",
    "milestones": [
      {
        "id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "title": "signingTheContract",
        "code": "prepayment",
        "type": "financing",
        "duration": {
          "days": 2,
          "type": "banking"
        },
        "sequenceNumber": 0,
        "percentage": 45.55
      },
      {
        "title": "deliveryOfGoods",
        "code": "postpayment",
        "type": "financing",
        "duration": {
          "days": 900,
          "type": "calendar"
        },
        "sequenceNumber": 0,
        "percentage": 54.45
      }
    ]
  }
}
bid = {
  "data": {
    "tenderers": [
      {
        "address": {
          "countryName": "Україна",
          "locality": "м. Вінниця",
          "postalCode": "21100",
          "region": "Вінницька область",
          "streetAddress": "вул. Островського, 33"
        },
        "contactPoint": {
          "email": "soleksuk@gmail.com",
          "name": "Сергій Олексюк",
          "telephone": "+380957777777"
        },
        "identifier": {
          "scheme": "UA-EDR",
          "id": "00137256",
          "uri": "http://www.sc.gov.ua/"
        },
        "name": "ДКП «Школяр»",
        "scale": "micro"
      }
    ],
    "value": {
      "amount": 500
    },
    "status": "draft"
  }
}

plan = {
    "tender": {
        "procurementMethod": "open",
        "procurementMethodType": "belowThreshold",
        "tenderPeriod": {"startDate": (now + timedelta(days=7)).isoformat()},
    },
    "items": [
        {
            "deliveryDate": {"endDate": (now + timedelta(days=15)).isoformat()},
            "additionalClassifications": [{"scheme": "ДКПП", "id": "01.11.92", "description": "Насіння гірчиці"}],
            "unit": {"code": "KGM", "name": "кг"},
            "classification": {"scheme": "ДК021", "description": "Mustard seeds", "id": "03111600-8"},
            "quantity": 1000,
            "description": "Насіння гірчиці",
        },
        {
            "deliveryDate": {"endDate": (now + timedelta(days=16)).isoformat()},
            "additionalClassifications": [{"scheme": "ДКПП", "id": "01.11.95", "description": "Насіння соняшнику"}],
            "unit": {"code": "KGM", "name": "кг"},
            "classification": {"scheme": "ДК021", "description": "Sunflower seeds", "id": "03111300-5"},
            "quantity": 2000,
            "description": "Насіння соняшнику",
        },
        {
            "deliveryDate": {"endDate": (now + timedelta(days=17)).isoformat()},
            "additionalClassifications": [{"scheme": "ДКПП", "id": "01.11.84", "description": "Насіння бавовнику"}],
            "unit": {"code": "KGM", "name": "кг"},
            "classification": {"scheme": "ДК021", "description": "Cotton seeds", "id": "03111400-6"},
            "quantity": 3000,
            "description": "Насіння бавовнику",
        },
    ],
    "classification": {"scheme": "ДК021", "description": "Seeds", "id": "03111000-2"},
    "additionalClassifications": [{"scheme": "КЕКВ", "id": "1", "description": "-"}],
    "procuringEntity": {
        "identifier": {"scheme": "UA-EDR", "id": "111983", "legalName": "ДП Державне Управління Справами"},
        "name": "ДУС",
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
        },
        "kind": "general",
    },
    "buyers": [
        {
            "identifier": {"scheme": "UA-EDR", "id": "111983", "legalName": "ДП Державне Управління Справами"},
            "name": "ДУС",
            "address": {
                "countryName": "Україна",
                "postalCode": "01220",
                "region": "м. Київ",
                "locality": "м. Київ",
                "streetAddress": "вул. Банкова, 11, корпус 1",
            },
            "kind": "general",
        }
    ],
    "budget": {
        "project": {"name": "proj_name", "id": "123"},
        "amount": 10000,
        "amountNet": 12222,
        "currency": "UAH",
        "id": "12303111000-2",
        "description": "budget_description",
        "period": {
            "startDate": datetime(year=now.year, month=1, day=1).isoformat(),
            "endDate": datetime(year=now.year, month=12, day=31).isoformat(),
        },
        "breakdown": [
            {
                "title": "other",
                "description": "Breakdown other description.",
                "value": {"amount": 1500, "currency": "UAH"},
            }
        ],
    },
}
