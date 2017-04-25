# -*- coding: utf-8 -*-
import json
import os
from datetime import timedelta
from hashlib import sha512
from copy import deepcopy

import openprocurement.tender.competitivedialogue.tests.base as base_test
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import PrefixedRequestClass
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUWebTest,
    BaseCompetitiveDialogUAStage2WebTest
)
from webtest import TestApp

test_tender_data_stage1 = {
  "tenderPeriod": {
    "endDate": "2016-02-11T14:04:18.962451"
  },
  "title": "Послуги шкільних їдалень",
  "title_en": "Services in school canteens",
  "minimalStep": {
    "currency": "UAH",
    "amount": 35
  },
  "procurementMethodType": "competitiveDialogueEU",
  "value": {
    "currency": "UAH",
    "amount": 500
  },
  "procuringEntity": {
    "kind": "general",
    "address": {
        "countryName": "Україна",
        "locality": "м. Вінниця",
        "postalCode": "21027",
        "region": "м. Вінниця",
        "streetAddress": "вул. Стахурського. 22"
    },
    "contactPoint": {
        "name": "Куца Світлана Валентинівна",
        "name_en": "Kutsa Svitlana V.",
        "telephone": "+380 (432) 46-53-02",
        "availableLanguage": u"uk",
        "url": "http://sch10.edu.vn.ua/"
    },
    "identifier": {
        "id": "21725150",
        "legalName": "Заклад \"Загальноосвітня школа І-ІІІ ступенів № 10 Вінницької міської ради\"",
        "legalName_en": "The institution \"Secondary school I-III levels № 10 Vinnitsa City Council\"",
        "scheme": "UA-EDR"
    },
    "name": "ЗОСШ #10 м.Вінниці",
    "name_en": "School #10 of Vinnytsia"
  },
  "items": [
    {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "description_en": "Services in school canteens",
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      },
      "quantity": 1
    }, {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "description_en": "Services in school canteens",
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "quantity": 1,
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      }
    }
  ]
}

test_tender_data_stage2_multiple_lots = {
  "procurementMethod": "selective",
  "dialogue_token": sha512('secret').hexdigest(),
  "title": "Послуги шкільних їдалень",
  "title_en": "Services in school canteens",
  "minimalStep": {
    "currency": "UAH",
    "amount": 35
  },
  "procurementMethodType": "competitiveDialogueEU.stage2",
  "value": {
    "currency": "UAH",
    "amount": 500
  },
  "shortlistedFirms": [
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137256',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "ДКП «Школяр»"
      },
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137226',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "ДКП «Книга»"
      },
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137228',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "«Кенгуру»",
      },
    ],
  "owner": "broker",
  "procuringEntity": {
    "kind": "general",
    "address": {
        "countryName": "Україна",
        "locality": "м. Вінниця",
        "postalCode": "21027",
        "region": "м. Вінниця",
        "streetAddress": "вул. Стахурського. 22"
    },
    "contactPoint": {
        "name": "Куца Світлана Валентинівна",
        "name_en": "Kutsa Svitlana V.",
        "telephone": "+380 (432) 46-53-02",
        "availableLanguage": u"uk",
        "url": "http://sch10.edu.vn.ua/"
    },
    "identifier": {
        "id": "21725150",
        "legalName": "Заклад \"Загальноосвітня школа І-ІІІ ступенів № 10 Вінницької міської ради\"",
        "legalName_en": "The institution \"Secondary school I-III levels № 10 Vinnitsa City Council\"",
        "scheme": "UA-EDR"
    },
    "name": "ЗОСШ #10 м.Вінниці",
    "name_en": "School #10 of Vinnytsia"
  },
  "items": [
    {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "description_en": "Services in school canteens",
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      },
      "quantity": 1
    }, {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "description_en": "Services in school canteens",
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "quantity": 1,
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      }
    }
  ]
}

test_tender_data_stage2EU = {
  "title": "Послуги шкільних їдалень",
  "title_en": "Services in school canteens",
  "procurementMethod": "selective",
  "minimalStep": {
    "currency": "UAH",
    "amount": 35
  },
  "status": "draft",
  "procurementMethodType": "competitiveDialogueEU.stage2",
  "value": {
    "currency": "UAH",
    "amount": 500
  },
  "dialogue_token": "",
  "shortlistedFirms": [
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137256',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "ДКП «Школяр»"
      },
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137226',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "ДКП «Книга»"
      },
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137228',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "«Кенгуру»",
      },
    ],
  "owner": "broker",
  "procuringEntity": {
    "kind": "general",
    "address": {
        "countryName": "Україна",
        "locality": "м. Вінниця",
        "postalCode": "21027",
        "region": "м. Вінниця",
        "streetAddress": "вул. Стахурського. 22"
    },
    "contactPoint": {
        "name": "Куца Світлана Валентинівна",
        "name_en": "Kutsa Svitlana V.",
        "telephone": "+380 (432) 46-53-02",
        "availableLanguage": u"uk",
        "url": "http://sch10.edu.vn.ua/"
    },
    "identifier": {
        "id": "21725150",
        "legalName": "Заклад \"Загальноосвітня школа І-ІІІ ступенів № 10 Вінницької міської ради\"",
        "legalName_en": "The institution \"Secondary school I-III levels № 10 Vinnitsa City Council\"",
        "scheme": "UA-EDR"
    },
    "name": "ЗОСШ #10 м.Вінниці",
    "name_en": "School #10 of Vinnytsia"
  },
  "items": [
    {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "description_en": "Services in school canteens",
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      },
      "quantity": 1
    }, {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "description_en": "Services in school canteens",
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "quantity": 1,
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      }
    }
  ]
}

test_tender_data_stage2UA = {
  "title": "футляри до державних нагород",
  "minimalStep": {
    "currency": "UAH",
    "amount": 35
  },
  "procurementMethod": "selective",
  "procurementMethodType": "competitiveDialogueUA.stage2",
  "value": {
    "currency": "UAH",
    "amount": 500
  },
  "status": "draft",
  "shortlistedFirms": [
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137256',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "ДКП «Школяр»"
      },
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137226',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "ДКП «Книга»"
      },
      {
          "identifier": {
              "scheme": u"UA-EDR",
              "id": u'00137228',
              "uri": u'http://www.sc.gov.ua/'
          },
          "name": "«Кенгуру»",
      },
  ],
  "owner": "broker",
  "procuringEntity": {
    "kind": "special",
    "address": {
        "countryName": "Україна",
        "locality": "м. Вінниця",
        "postalCode": "21027",
        "region": "м. Вінниця",
        "streetAddress": "вул. Стахурського. 22"
    },
    "contactPoint": {
        "name": "Куца Світлана Валентинівна",
        "telephone": "+380 (432) 46-53-02",
        "url": "http://sch10.edu.vn.ua/"
    },
    "identifier": {
        "id": "21725150",
        "legalName": "Заклад \"Загальноосвітня школа І-ІІІ ступенів № 10 Вінницької міської ради\"",
        "scheme": "UA-EDR"
    },
    "name": "ЗОСШ #10 м.Вінниці"
  },
  "items": [
    {
      "unit": {
        "code": "44617100-9",
        "name": "item"
      },
      "additionalClassifications": [
        {
          "scheme": "ДКПП",
          "id": "17.21.1",
          "description": "Послуги шкільних їдалень"
        }
      ],
      "description": "Послуги шкільних їдалень",
      "deliveryDate": {
            "startDate": (get_now() + timedelta(days=20)).isoformat(),
            "endDate": (get_now() + timedelta(days=50)).isoformat()
      },
      "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
      },
      "classification": {
        "scheme": "CPV",
        "id": "37810000-9",
        "description": "Test"
      },
      "quantity": 1
    }
  ]
}

test_tender_data_stage1["tenderPeriod"] = {
    "endDate": (get_now() + timedelta(days=31)).isoformat()
}

bid = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Вінниця",
                    "postalCode": "21100",
                    "region": "м. Вінниця",
                    "streetAddress": "вул. Островського, 33"
                },
                "contactPoint": {
                    "email": "soleksuk@gmail.com",
                    "name": "Сергій Олексюк",
                    "telephone": "+380 (432) 21-69-30"
                },
                "identifier": {
                    "scheme": u"UA-EDR",
                    "id": u"00137256",
                    "uri": u"http://www.sc.gov.ua/"
                },
                "name": "ДКП «Школяр»"
            }
        ],
        "status": "draft",
        "subcontractingDetails": "ДКП «Орфей», Україна",
        'selfEligible': True,
        'selfQualified': True,
    }
}

bid_stage2 = deepcopy(bid)
bid_stage2["data"]["value"] = {"amount": 500}

bid_with_bad_participant = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Львів",
                    "postalCode": "21100",
                    "region": "м. Львів",
                    "streetAddress": "вул. Поле, 33"
                },
                "contactPoint": {
                    "email": "pole@gmail.com",
                    "name": "Вільям Поле",
                    "telephone": "+380 (452) 21-69-31"
                },
                "identifier": {
                    "id": "00137230",
                    "legalName": "ТОВ Бур",
                    "scheme": "UA-EDR",
                    "uri": "http://pole.edu.vn.ua/"
                },
                "name": "ТОВ \"Бур\""
            },
        ],
        "value": {
            "amount": 500
        },
        "status": "draft",
        "subcontractingDetails": "ДКП «Орфей», Україна",
        'selfEligible': True,
        'selfQualified': True,
    }
}
bid2 = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Львів",
                    "postalCode": "79013",
                    "region": "м. Львів",
                    "streetAddress": "вул. Островського, 34"
                },
                "contactPoint": {
                    "email": "aagt@gmail.com",
                    "name": "Андрій Олексюк",
                    "telephone": "+380 (322) 91-69-30"
                },
                "identifier": {
                    "scheme": u"UA-EDR",
                    "id": u"00137226",
                    "uri": u"http://www.sc.gov.ua/"
                },
                "name": "ДКП «Книга»"
            }
        ],
        "value": {
            "amount": 499
        },
        'selfEligible': True,
        'selfQualified': True,
    }
}

bid3 = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Львів",
                    "postalCode": "79013",
                    "region": "м. Львів",
                    "streetAddress": "вул. Островського, 35"
                },
                "contactPoint": {
                    "email": "fake@mail.com",
                    "name": "Іван Іваненко",
                    "telephone": "+380 (322) 12-34-56"
                },
                "identifier": {
                    "scheme": u"UA-EDR",
                    "id": u"00137227",
                    "uri": u"http://www.sc.gov.ua/"
                },
                "name": "«Снігур»"
            }
        ],
        "value": {
            "amount": 5
        },
        'selfEligible': True,
        'selfQualified': True,
    }
}

bid4 = {
    "data": {
        "tenderers": [
            {
                "address": {
                    "countryName": "Україна",
                    "locality": "м. Запоріжя",
                    "postalCode": "79013",
                    "region": "м. Запоріжжя",
                    "streetAddress": "вул. Коцюбинського, 15"
                },
                "contactPoint": {
                    "email": "fake@mail.com",
                    "name": "Іван Карпенко",
                    "telephone": "+380 (322) 12-34-56"
                },
                "identifier": {
                    "scheme": u"UA-EDR",
                    "id": u"00137228",
                    "uri": u"http://www.sc.gov.ua/"
                },
                "name": "«Кенгуру»"
            }
        ],
        "value": {
            "amount": 5
        },
        'selfEligible': True,
        'selfQualified': True,
    }
}

bid2_with_docs = deepcopy(bid2)

bid2_with_docs["data"]["documents"] = [
     {
         'title': u'Proposal_part1.pdf',
         'url': u"http://broken1.ds",
         'hash': 'md5:' + '0' * 32,
         'format': 'application/pdf',
     }
 ]

bid4_with_docs = deepcopy(bid4)

bid4_with_docs["data"]["documents"] = [
     {
         'title': u'Proposal_part1.pdf',
         'url': u"http://broken1.ds",
         'hash': 'md5:' + '0' * 32,
         'format': 'application/pdf',
     },
     {
         'title': u'Proposal_part2.pdf',
         'url': u"http://broken2.ds",
         'hash': 'md5:' + '0' * 32,
         'format': 'application/pdf',
         'confidentiality': 'buyerOnly',
         'confidentialityRationale': 'Only our company sells badgers with pink hair.',
     }
 ]

question = {
    "data": {
        "author": {
            "address": {
                "countryName": "Україна",
                "locality": "м. Вінниця",
                "postalCode": "21100",
                "region": "м. Вінниця",
                "streetAddress": "вул. Островського, 33"
            },
            "contactPoint": {
                "email": "soleksuk@gmail.com",
                "name": "Сергій Олексюк",
                "telephone": "+380 (432) 21-69-30"
            },
            "identifier": {
                "id": "00137226",
                "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
                "scheme": "UA-EDR",
                "uri": "http://sch10.edu.vn.ua/"
            },
            "name": "ДКП «Школяр»"
        },
        "description": "Просимо додати таблицю потрібної калорійності харчування",
        "title": "Калорійність"
    }
}

question_with_bad_participant = {
    "data": {
        "author": {
            "address": {
                "countryName": "Україна",
                "locality": "м. Львів",
                "postalCode": "21100",
                "region": "м. Львів",
                "streetAddress": "вул. Поле, 33"
            },
            "contactPoint": {
                "email": "pole@gmail.com",
                "name": "Вільям Поле",
                "telephone": "+380 (452) 21-69-31"
            },
            "identifier": {
                "id": "00137230",
                "legalName": "ТОВ Бур",
                "scheme": "UA-EDR",
                "uri": "http://pole.edu.vn.ua/"
            },
            "name": "ТОВ \"Бур\""
        },
        "description": "Просимо додати таблицю потрібної калорійності харчування",
        "title": "Калорійність"
    }
}

answer = {
    "data": {
        "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
    }
}

cancellation = {
    'data': {
        'reason': 'cancellation reason'
    }
}

complaint = {
    "data": {
        "author": {
            "address": {
                "countryName": "Україна",
                "locality": "м. Вінниця",
                "postalCode": "21100",
                "region": "м. Вінниця",
                "streetAddress": "вул. Островського, 33"
            },
            "contactPoint": {
                "email": "soleksuk@gmail.com",
                "name": "Сергій Олексюк",
                "telephone": "+380 (432) 21-69-30"
            },
            "identifier": {
                "id": "13313462",
                "legalName": "Державне комунальне підприємство громадського харчування «Школяр»",
                "scheme": "UA-EDR",
                "uri": "http://sch10.edu.vn.ua/"
            },
            "name": "ДКП «Школяр»"
        },
        "description": "Умови виставлені замовником не містять достатньо інформації, щоб заявка мала сенс.",
        "title": "Недостатньо інформації"
    }
}

test_lots = [
    {
        'title': 'Лот №1',
        'description': 'Опис Лот №1',
        'value': test_tender_data_stage1['value'],
        'minimalStep': test_tender_data_stage1['minimalStep'],
    },
    {
        'title': 'Лот №2',
        'description': 'Опис Лот №2',
        'value': test_tender_data_stage1['value'],
        'minimalStep': test_tender_data_stage1['minimalStep'],
    }
]


class DumpsTestAppwebtest(TestApp):
    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "api-sandbox.openprocurement.org"
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                            'DATA:\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                except ValueError:
                    pass  # doesn't write anything
                self.file_obj.write("\n")
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            headers = [(n.title(), v)
                       for n, v in resp.headerlist
                       if n.lower() != 'content-length']
            headers.sort()
            self.file_obj.write(str('Response: %s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write(json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except ValueError:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TenderResourceTest(BaseCompetitiveDialogEUWebTest):
    initial_data = test_tender_data_stage1
    docservice = True

    def setUp(self):
        self.app = DumpsTestAppwebtest("config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()
            self.app.app.registry.docservice_url = 'http://public.docs-sandbox.openprocurement.org'

    def generate_docservice_url(self):
        return super(TenderResourceTest, self).generate_docservice_url().replace(
            '/localhost/', '/public.docs-sandbox.openprocurement.org/'
        )

    def test_stage1(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules
        #

        # Write empty listing
        with open('docs/source/tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        # Try send bad data
        with open('docs/source/tutorial/tender-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/tender-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post(request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        #### Creating tender
        #

        # Create tender
        with open('docs/source/tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data_stage1})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']

        # Check tender
        with open('docs/source/tutorial/blank-tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        # Get tender without auth
        with open('docs/source/tutorial/tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender
        #

        # Update endDate
        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open('docs/source/tutorial/patch-items-value-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data':
                {
                    "tenderPeriod": {
                        "endDate": tenderPeriod_endDate.isoformat()
                    }
                }
            })

        # Show listing after tender patch
        with open('docs/source/tutorial/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        self.tender_id = tender['id']

        # Setting Bid guarantee
        #

        # Set bit guarantee
        with open('docs/source/tutorial/set-bid-guarantee.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'guarantee': {'amount': 8, 'currency': 'USD'}}})
            self.assertEqual(response.status, '200 OK')
            self.assertIn('guarantee', response.json['data'])

        #### Uploading documentation
        #

        with open('docs/source/tutorial/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open('docs/source/tutorial/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open('docs/source/tutorial/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                                    upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries
        #

        with open('docs/source/tutorial/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), question, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(
                self.tender_id, question_id, owner_token), answer, status=200)
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(
                self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(
                self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.time_shift('enquiryPeriod_ends')
        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {'value': {'amount': 501.0}}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), question, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {'value': {'amount': 501,
                                                               'currency': u'UAH'},
                                                     'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}
                                                     }
                                            })
            self.assertEqual(response.status, '200 OK')

        #### Registering bid
        #

        bids_access = {}
        with open('docs/source/tutorial/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid)
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id,
                                                                                     bid1_id,
                                                                                     bids_access[bid1_id]),
                                           {'data': {'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading
        #

        with open('docs/source/tutorial/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                         bid1_id,
                                                                                         bids_access[bid1_id]),
                                     upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/upload-bid-descriptive-decision-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                         bid1_id,
                                                                                         bids_access[bid1_id]),
                                     upload_files=[('file', 'DescriptiveProposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        priv_doc_id1 = response.json['data']['id']

        # set confidentiality properties
        with open('docs/source/tutorial/mark-bid-doc-decision-proposal.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                self.tender_id, bid1_id, priv_doc_id1, bids_access[bid1_id]),
                {'data': {'isDescriptionDecision': True}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                         bid1_id,
                                                                                         bids_access[bid1_id]),
                                     upload_files=[('file', 'Proposal_top_secrets.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')
            priv_doc_id = response.json['data']['id']

        # set confidentiality properties
        with open('docs/source/tutorial/mark-bid-doc-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]),
                {'data': {'confidentiality': 'buyerOnly',
                          'confidentialityRationale': 'Only our company sells badgers with pink hair.'}
                 })
            self.assertEqual(response.status, '200 OK')

        # set confidentiality properties
        with open('docs/source/tutorial/mark-bid-doc-decision-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                self.tender_id, bid1_id, priv_doc_id1, bids_access[bid1_id]),
                {'data': {'confidentiality': 'buyerOnly'}})
            self.assertEqual(response.status, '200 OK')

        # set confidentiality properties
        with open('docs/source/tutorial/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation
        #

        with open('docs/source/tutorial/bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation
        #

        with open('docs/source/tutorial/bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                {'data': {'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/register-3rd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid3)
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/register-4rd-bidder.http', 'w') as self.app.file_obj:
            for document in bid4_with_docs['data']['documents']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid4_with_docs)
            bid4_id = response.json['data']['id']
            bids_access[bid4_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        # Pre-qualification

        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open('docs/source/tutorial/qualifications-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            qualifications = response.json['data']
            self.assertEqual(len(qualifications), 4)
            self.assertEqual(qualifications[0]['bidID'], bid1_id)
            self.assertEqual(qualifications[1]['bidID'], bid2_id)
            self.assertEqual(qualifications[2]['bidID'], bid3_id)
            self.assertEqual(qualifications[3]['bidID'], bid4_id)

        with open('docs/source/tutorial/approve-qualification1.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualifications[0]['id'],
                                                                                               owner_token),
                                           {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')
        with open('docs/source/tutorial/approve-qualification2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualifications[1]['id'],
                                                                                               owner_token),
                                           {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualifications[2]['id'],
                                                                                               owner_token),
                                           {'data': {'status': 'unsuccessful'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/approve-qualification4.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualifications[3]['id'],
                                                                                               owner_token),
                                           {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualificated-bids-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/rejected-bid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        # active.pre-qualification.stand-still

        with open('docs/source/tutorial/pre-qualification-confirmation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'status': 'active.pre-qualification.stand-still'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        ###### Pending

        self.set_status('active.stage2.pending', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open('docs/source/tutorial/stage2-pending.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.pending')

        with open('docs/source/tutorial/stage2-waiting.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'status': 'active.stage2.waiting'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.waiting')

        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        test_tender_data_stage2EU['dialogue_token'] = sha512(owner_token).hexdigest()
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data_stage2EU})
        self.assertEqual(response.status, '201 Created')
        new_tender_id = response.json['data']['id']
        self.new_tender_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token),
                                       {'data': {'status': 'draft.stage2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'draft.stage2')

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                            {'data': {'stage2TenderID': new_tender_id,
                                      'status': 'complete'}})

        self.app.authorization = auth

        with open('docs/source/tutorial/tender_stage1_complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'complete')
            self.assertEqual(response.json['data']['stage2TenderID'], new_tender_id)

        with open('docs/source/tutorial/tender_stage2_get_token.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/credentials?acc_token={}'.format(new_tender_id, owner_token),
                                           {})
            self.assertEqual(response.status, '200 OK')
            self.new_tender_token = response.json['access']['token']

        with open('docs/source/tutorial/tender_stage2_modify_status.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token),
                                           {'data': {'status': 'active.tendering'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.tendering')

    def test_stage2_EU(self):
        request_path = '/tenders?opt_pretty=1'

        #### Creating tender
        #

        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        test_tender_data_stage2EU['dialogue_token'] = sha512("super_secret_token").hexdigest()
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data_stage2EU})
        self.assertEqual(response.status, '201 Created')
        self.tender_id = response.json['data']['id']
        tender = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                       {'data': {'status': 'draft.stage2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'draft.stage2')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender
        #

        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open('docs/source/tutorial/stage2/EU/patch-tender-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}}})

        with open('docs/source/tutorial/stage2/EU/tender-activate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'status': 'active.tendering'}})

        response = self.app.get('/tenders')
        with open('docs/source/tutorial/stage2/EU/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders')
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Uploading documentation
        #

        with open('docs/source/tutorial/stage2/EU/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open('docs/source/tutorial/stage2/EU/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open('docs/source/tutorial/stage2/EU/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                   doc_id,
                                                                                   owner_token),
                                    upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries
        #

        with open('docs/source/tutorial/stage2/EU/ask-question-bad-participant.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                          question_with_bad_participant,
                                          status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/stage2/EU/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), question, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/EU/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(
                self.tender_id, question_id, owner_token), answer, status=200)
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.time_shift('enquiryPeriod_ends')
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender['id'], owner_token))
        with open('docs/source/tutorial/stage2/EU/update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            endDate = (get_now() + timedelta(days=30, seconds=10)).isoformat()
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {'items': [{'deliveryDate': {"endDate": endDate}}]}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/stage2/EU/ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(
                self.tender_id), question, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/stage2/EU/update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {
                                               'items': [{'deliveryDate': {'endDate': endDate}}],
                                               'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}
                                           }})
            self.assertEqual(response.status, '200 OK')


        #### Registering bid
        #

        bids_access = {}

        with open('docs/source/tutorial/stage2/EU/try-register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid_with_bad_participant,
                                          status=403)

        with open('docs/source/tutorial/stage2/EU/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid_stage2)
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/EU/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]), {"data": {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading
        #

        with open('docs/source/tutorial/stage2/EU/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]), upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/EU/upload-bid-private-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'Proposal_top_secrets.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')
            priv_doc_id = response.json['data']['id']

        # set confidentiality properties
        with open('docs/source/tutorial/stage2/EU/mark-bid-doc-private.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
                self.tender_id, bid1_id, priv_doc_id, bids_access[bid1_id]),
                {'data': {'confidentiality': 'buyerOnly',
                          'confidentialityRationale': 'Only our company sells badgers with pink hair.'}})
            self.assertEqual(response.status, '200 OK')

        # set confidentiality properties
        with open('docs/source/tutorial/stage2/EU/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/upload-bid-financial-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'financial_doc.pdf', '1000$')])
            self.assertEqual(response.status, '201 Created')
            financial_doc_id = response.json['data']['id']

        response = self.app.post('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]), upload_files=[('file', 'financial_doc2.pdf', '1000$')])
        self.assertEqual(response.status, '201 Created')
        financial_doc_id = response.json['data']['id']

        with open('docs/source/tutorial/stage2/EU/bidder-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/financial_documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/upload-bid-qualification-document-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/qualification_documents?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]),
                upload_files=[('file', 'qualification_document.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/EU/bidder-view-financial-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')


        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation
        #

        with open('docs/source/tutorial/stage2/EU/bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation
        #

        with open('docs/source/tutorial/stage2/EU/bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]), {'data': {"status": "pending"}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/register-2nd-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        bid4_with_docs["data"]["eligibilityDocuments"] = [
          {
            'title': u'eligibility_doc.pdf',
            'url': u"http://broken3.ds",
            'hash': 'md5:' + '0' * 32,
            'format': 'application/pdf'
          }
        ]

        bid4_with_docs["data"]["financialDocuments"] = [
          {
            'title': u'financial_doc.pdf',
            'url': u"http://broken4.ds",
            'hash': 'md5:' + '0' * 32,
            'format': 'application/pdf'
          }
        ]

        bid4_with_docs["data"]["qualificationDocuments"] = [
          {
            'title': u'qualification_document.pdf',
            'url': u"http://broken5.ds",
            'hash': 'md5:' + '0' * 32,
            'format': 'application/pdf'
          }
        ]
        with open('docs/source/tutorial/stage2/EU/register-3rd-bidder.http', 'w') as self.app.file_obj:
            for document in bid4_with_docs['data']['documents']:
                document['url'] = self.generate_docservice_url()
            for document in bid4_with_docs['data']['eligibilityDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid4_with_docs['data']['financialDocuments']:
                document['url'] = self.generate_docservice_url()
            for document in bid4_with_docs['data']['qualificationDocuments']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid4_with_docs)
            bid3_id = response.json['data']['id']
            bids_access[bid3_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        # Pre-qualification

        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open('docs/source/tutorial/stage2/EU/qualifications-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            qualifications = response.json['data']['qualifications']
            self.assertEqual(len(qualifications), 3)
            self.assertEqual(qualifications[0]['bidID'], bid1_id)
            self.assertEqual(qualifications[1]['bidID'], bid2_id)
            self.assertEqual(qualifications[2]['bidID'], bid3_id)

        with open('docs/source/tutorial/stage2/EU/approve-qualification1.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualifications[0]['id'], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")
        with open('docs/source/tutorial/stage2/EU/approve-qualification2.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualifications[1]['id'], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        with open('docs/source/tutorial/stage2/EU/reject-qualification3.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualifications[2]['id'], owner_token), {"data": {"status": "unsuccessful"}})
            self.assertEqual(response.status, "200 OK")

        with open('docs/source/tutorial/stage2/EU/qualificated-bids-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        with open('docs/source/tutorial/stage2/EU/rejected-bid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid3_id, owner_token))
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still

        with open('docs/source/tutorial/stage2/EU/pre-qualification-confirmation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'status': 'active.pre-qualification.stand-still'}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        #### Auction

        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        patch_data = {
            'auctionUrl': u'http://auction-sandbox.openprocurement.org/tenders/{}'.format(self.tender_id),
            'bids': [
                {
                    "id": bid1_id,
                    "participationUrl": u'http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}'.format(self.tender_id, bid1_id)
                },
                {
                    "id": bid2_id,
                    "participationUrl": u'http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}'.format(self.tender_id, bid2_id)
                },
                {
                    "id": bid3_id
                }

            ]
        }
        response = self.app.patch_json('/tenders/{}/auction?acc_token={}'.format(self.tender_id, owner_token),
                                       {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/stage2/EU/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        #### Confirming qualification
        #
        # self.set_status('active.qualification')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                      {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open('docs/source/tutorial/stage2/EU/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                                {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open('docs/source/tutorial/stage2/EU/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                {'data': {'contractNumber': 'contract#1', 'value': {'amount': 238}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Setting contract signature date
        #

        with open('docs/source/tutorial/stage2/EU/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                {'data': {'dateSigned': get_now().isoformat()} })
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {'period': {'startDate': (get_now()).isoformat(),
                                   'endDate': (get_now() + timedelta(days=365)).isoformat()}}
        with open('docs/source/tutorial/stage2/EU/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, self.contract_id, owner_token), {'data': {'period': period_dates['period']}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation
        #

        with open('docs/source/tutorial/stage2/EU/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_first_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/EU/tender-contract-get-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/tender-contract-upload-second-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_second_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open('docs/source/tutorial/stage2/EU/tender-contract-patch-document.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}/documents/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, self.document_id, owner_token),
                {'data': {'language': 'en',
                          'title_en': 'Title of Document',
                          'description_en': 'Description of Document'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/tender-contract-get-documents-again.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}/documents'.format(
                self.tender_id, self.contract_id))
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/tender-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request
        #

        with open('docs/source/tutorial/stage2/EU/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token), cancellation)
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open('docs/source/tutorial/stage2/EU/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, owner_token),
                {"data": {'reasonType': 'unsuccessful'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation
        #

        with open('docs/source/tutorial/stage2/EU/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/EU/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}} )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/EU/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token), upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        #

        with open('docs/source/tutorial/stage2/EU/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data":{"status":"active"}})
            self.assertEqual(response.status, '200 OK')

    def test_cancel_tender(self):

        #### Creating tender
        #

        # Create tender
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data_stage1})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # Check tender
        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')

        # Get tender without auth
        self.app.authorization = None
        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Preparing the cancellation request
        #

        with open('docs/source/tutorial/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token), cancellation)
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open('docs/source/tutorial/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data": {'reasonType': 'unsuccessful'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation
        #

        with open('docs/source/tutorial/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token), {'data': {"description": 'Changed description'}} )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, cancellation_doc_id, owner_token), upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        #

        with open('docs/source/tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')

    def test_complaints(self):
        response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data_stage1})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        with open('docs/source/tutorial/complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint)
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open('docs/source/tutorial/complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/complaints/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                               complaint1_id,
                                                                                               complaint1_token),
                                     upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.not_json = True
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/complaint-claim.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id,
                                                                                           complaint1_id,
                                                                                           complaint1_token),
                                           {'data': {'status': 'claim'}})
            self.assertEqual(response.status, '200 OK')

        claim = {'data': complaint['data'].copy()}
        claim['data']['status'] = 'claim'
        with open('docs/source/tutorial/complaint-submission-claim.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), claim)
            self.assertEqual(response.status, '201 Created')

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        complaint_data = {'data': complaint['data'].copy()}
        complaint_data['data']['status'] = 'pending'
        with open('docs/source/tutorial/complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint3_id = response.json['data']['id']
        complaint3_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), claim)
        self.assertEqual(response.status, '201 Created')
        complaint4_id = response.json['data']['id']
        complaint4_token = response.json['access']['token']

        with open('docs/source/tutorial/complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, complaint1_id, complaint1_token),
                {'data': {'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-answer.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, complaint2_id, owner_token),
                {'data': {'status': 'answered',
                          'resolutionType': 'resolved',
                          'resolution': 'Виправлено неконкурентні умови'}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, complaint4_id, owner_token),
            {'data': {'status': 'answered',
                      'resolutionType': 'invalid',
                      'resolution': 'Вимога не відповідає предмету закупівлі'}
             })
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-satisfy.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, complaint2_id, complaint2_token),
                {'data': {'satisfied': True, 'status': 'resolved'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-escalate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, complaint4_id, complaint4_token),
                {'data': {'satisfied': False, 'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_id = response.json['data']['id']
        complaint5_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint6_id = response.json['data']['id']
        complaint6_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint4_id),
                                           {'data': {'status': 'invalid'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id),
                                           {'data': {'status': 'accepted'}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id),
                                       {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id),
                                       {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id),
                                       {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/complaints/{}/documents'.format(self.tender_id, complaint1_id),
                                     upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id),
                                           {'data': {'status': 'satisfied'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint3_id),
                                           {'data': {'status': 'declined'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint5_id),
                                           {'data': {'decision': 'Тендер скасовується замовником',
                                                     'status': 'stopped'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id,
                                                                                           complaint1_id,
                                                                                           owner_token),
                                           {'data': {'tendererAction': 'Умови виправлено','status': 'resolved'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(self.tender_id,
                                                                                           complaint6_id,
                                                                                           complaint6_token),
                                           {'data': {'cancellationReason': 'Тендер скасовується замовником',
                                                     'status': 'stopping'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}'.format(self.tender_id, complaint6_id),
                                           {'data': {'decision': 'Тендер скасовується замовником',
                                                     'status': 'stopped'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id), complaint)
        self.assertEqual(response.status, '201 Created')
        complaint7_id = response.json['data']['id']
        complaint7_token = response.json['access']['token']

        with open('docs/source/tutorial/complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, complaint7_id, complaint7_token),
                {'data': {'cancellationReason': 'Умови виправлено', 'status': 'cancelled'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/complaints/{}'.format(self.tender_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_qualification_complaints(self):
        response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data_stage1})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.tender_id = tender['id']

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid)
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token),
                                       {'data': {'status': 'pending'}})

        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)

        # create third bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid3)

        # Pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        qualification_id = qualifications[0]['id']

        with open('docs/source/tutorial/qualification-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token), complaint)
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open('docs/source/tutorial/qualification-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}'.format(
                self.tender_id, qualification_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/qualification-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, qualification_id, complaint1_id, complaint1_token),
                {'data': {'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint['data'].copy()}
        complaint_data['data']['status'] = 'pending'
        with open('docs/source/tutorial/qualification-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
                self.tender_id, qualification_id, bid_token), complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id, qualification_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint3_token = response.json['access']['token']
        complaint3_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id, qualification_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id, qualification_id, bid_token), complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_token = response.json['access']['token']
        complaint5_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(
            self.tender_id, qualification_id, bid_token), complaint)
        self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/qualification-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, qualification_id, response.json['data']['id'], response.json['access']['token']),
                {'data': {'cancellationReason': 'Умови виправлено', 'status': 'cancelled'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/qualification-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint2_id), {'data': {'status': 'invalid'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint1_id), {'data': {'status': 'accepted'}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
            self.tender_id, qualification_id, complaint3_id), {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
            self.tender_id, qualification_id, complaint4_id), {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
            self.tender_id, qualification_id, complaint5_id), {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/qualifications/{}/complaints/{}/documents'.format(
                self.tender_id, qualification_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/qualification-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint1_id), {'data': {'status': 'satisfied'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint3_id), {'data': {'status': 'declined'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint5_id),
                {'data': {'decision': 'Тендер скасовується замовником', 'status': 'stopped'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/qualification-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, qualification_id, complaint1_id, owner_token),
                {'data': {'tendererAction': 'Умови виправлено', 'status': 'resolved'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, qualification_id, complaint4_id, complaint4_token),
                {'data': {'cancellationReason': 'Тендер скасовується замовником', 'status': 'stopping'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/qualification-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint4_id),
                {'data': {'decision': 'Тендер скасовується замовником', 'status': 'stopped'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = None
        with open('docs/source/tutorial/qualification-complaints-list.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications/{}/complaints'.format(self.tender_id, qualification_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/qualification-complaint.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications/{}/complaints/{}'.format(
                self.tender_id, qualification_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

    def test_multiple_lots(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules
        #

        with open('docs/source/multiple_lots_tutorial/tender-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        #### Creating tender
        #
        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/multiple_lots_tutorial/tender-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data_stage1})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots
        with open('docs/source/multiple_lots_tutorial/tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[1]})
        self.assertEqual(response.status, '201 Created')
        lot_id2 = response.json['data']['id']

        # add relatedLot for item
        with open('docs/source/multiple_lots_tutorial/tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                           {'data': {'items': [{'relatedLot': lot_id1}, {'relatedLot': lot_id2}]}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/multiple_lots_tutorial/tender-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/multiple_lots_tutorial/tender-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/multiple_lots_tutorial/bid-lot1.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': bid['data']["tenderers"],
                                                    'lotValues': [{'subcontractingDetails': 'ДКП «Орфей», Україна',
                                                                   'relatedLot': lot_id1}]}})
            self.assertEqual(response.status, '201 Created')
            bid1_token = response.json['access']['token']
            bid1_id = response.json['data']['id']

        with open('docs/source/multiple_lots_tutorial/bid-lot2.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': bid2['data']['tenderers'],
                                                    'lotValues': [{'relatedLot': lot_id1},
                                                                  {'subcontractingDetails': 'ДКП «Укр Прінт», Україна',
                                                                   'relatedLot': lot_id2}]}})
            self.assertEqual(response.status, '201 Created')
            bid2_id = response.json['data']['id']
            bid2_token = response.json['access']['token']

        with open('docs/source/multiple_lots_tutorial/bid-lot2.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': bid3['data']['tenderers'],
                                                    'lotValues': [{'relatedLot': lot_id1},
                                                                  {'subcontractingDetails': 'ДКП «Укр Прінт», Україна',
                                                                   'relatedLot': lot_id2}]}})
            self.assertEqual(response.status, '201 Created')
            bid3_id = response.json['data']['id']
            bid3_token = response.json['access']['token']

        with open('docs/source/multiple_lots_tutorial/tender-invalid-all-bids.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender_id, lot_id2, owner_token),
                                           {'data': {'value': {'amount': 400}}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/multiple_lots_tutorial/bid-lot1-invalid-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/multiple_lots_tutorial/bid-lot1-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token),
                                           {'data': {'lotValues': [{'subcontractingDetails': 'ДКП «Орфей»',
                                                                    'relatedLot': lot_id1}],
                                                     'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/multiple_lots_tutorial/bid-lot2-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid2_id, bid2_token),
                                           {'data': {'lotValues': [{'relatedLot': lot_id1}],
                                                     'status': 'pending'}})

        with open('docs/source/multiple_lots_tutorial/bid-lot3-update-view.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid3_id, bid3_token),
                                           {'data': {'lotValues': [{'relatedLot': lot_id1}],
                                                     'status': 'pending'}})

            self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        with open('docs/source/multiple_lots_tutorial/tender-view-pre-qualification.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/multiple_lots_tutorial/qualifications-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.content_type, 'application/json')
            qualifications = response.json['data']

        with open('docs/source/multiple_lots_tutorial/tender-activate-qualifications.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualifications[0]['id'], owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
            self.tender_id, qualifications[1]['id'], owner_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
            self.tender_id, qualifications[2]['id'], owner_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        with open('docs/source/multiple_lots_tutorial/tender-view-pre-qualification-stand-still.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                           {'data': {'status': 'active.pre-qualification.stand-still'}})
            self.assertEqual(response.status, "200 OK")

        ###### Pending

        self.set_status('active.stage2.pending',
                        {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        with open('docs/source/multiple_lots_tutorial/stage2-pending.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.pending')

        with open('docs/source/multiple_lots_tutorial/stage2-waiting.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'status': 'active.stage2.waiting'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.stage2.waiting')

        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        # Update firms after adding lots
        test_tender_data_stage2_multiple_lots['lots'] = response.json['data']['lots']
        test_tender_data_stage2_multiple_lots['items'] = response.json['data']['items']
        test_tender_data_stage2_multiple_lots['shortlistedFirms'][0]['lots'] = [{'id': lot_id1}]
        test_tender_data_stage2_multiple_lots['shortlistedFirms'][1]['lots'] = [{'id': lot_id1}, {'id': lot_id2}]
        test_tender_data_stage2_multiple_lots['shortlistedFirms'][2]['lots'] = [{'id': lot_id1}, {'id': lot_id2}]

        test_tender_data_stage2EU['dialogue_token'] = sha512(owner_token).hexdigest()
        response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data_stage2_multiple_lots})
        self.assertEqual(response.status, '201 Created')
        new_tender_id = response.json['data']['id']
        self.new_tender_token = response.json['access']['token']

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                            {'data': {'stage2TenderID': new_tender_id,
                                      'status': 'complete'}})

        self.app.authorization = auth

        with open('docs/source/multiple_lots_tutorial/tender_stage1_complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'complete')
            self.assertEqual(response.json['data']['stage2TenderID'], new_tender_id)

        with open('docs/source/multiple_lots_tutorial/tender_stage2_modify_status.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token),
                                           {'data': {'status': 'active.tendering'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.tendering')

        with open('docs/source/multiple_lots_tutorial/show_stage2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}?acc_token={}'.format(new_tender_id, self.new_tender_token))

            self.assertEqual(response.status, '200 OK')

        # user which wasn't allowed on first stage can't create bid on second
        with open('docs/source/multiple_lots_tutorial/register_bad_bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(new_tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': bid_with_bad_participant['data']['tenderers'],
                                                    'lotValues': [{'subcontractingDetails': 'ДКП «Орфей», Україна',
                                                                   'value': {'amount': 500}, 'relatedLot': lot_id1}]}},
                                          status=403)

        # user can create bid
        with open('docs/source/multiple_lots_tutorial/register_ok_bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(new_tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': bid['data']['tenderers'],
                                                    'lotValues': [{'subcontractingDetails': 'ДКП «Орфей», Україна',
                                                                   'value': {'amount': 500}, 'relatedLot': lot_id1}]}},
                                          status=201)

        # user can't create bid on lot which he wasn't allowed
        with open('docs/source/multiple_lots_tutorial/register_bad_not_allowed_lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(new_tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': bid['data']['tenderers'],
                                                    'lotValues': [{'subcontractingDetails': 'ДКП «Орфей», Україна',
                                                                   'value': {'amount': 300}, 'relatedLot': lot_id2}]}},
                                          status=403)

    def test_award_complaints_stage2(self):
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        test_tender_data_stage2EU['dialogue_token'] = sha512("super_secret_token").hexdigest()
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data_stage2EU})
        self.assertEqual(response.status, '201 Created')
        self.tender_id = response.json['data']['id']
        tender = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                       {'data': {'status': 'draft.stage2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'draft.stage2')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                      {'data': {'status': 'active.tendering'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid_stage2)
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token),
                                       {'data': {'status': 'pending'}})
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2)

        # Pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = auth

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], owner_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token), complaint)
            self.assertEqual(response.status, '201 Created')

        complaint1_token = response.json['access']['token']
        complaint1_id = response.json['data']['id']

        with open('docs/source/tutorial/award-complaint-submission-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
                self.tender_id, award_id, complaint1_id, complaint1_token),
                upload_files=[('file', u'Complaint_Attachement.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-complaint.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_id, complaint1_id, complaint1_token), {'data': {'status': 'pending'}})
            self.assertEqual(response.status, '200 OK')

        complaint_data = {'data': complaint['data'].copy()}
        complaint_data['data']['status'] = 'pending'
        with open('docs/source/tutorial/award-complaint-submission-complaint.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_id, bid_token),
                complaint_data)
            self.assertEqual(response.status, '201 Created')

        complaint2_token = response.json['access']['token']
        complaint2_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, award_id, bid_token),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint3_token = response.json['access']['token']
        complaint3_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, award_id, bid_token),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint4_token = response.json['access']['token']
        complaint4_id = response.json['data']['id']

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, award_id, bid_token),
            complaint_data)
        self.assertEqual(response.status, '201 Created')
        complaint5_token = response.json['access']['token']
        complaint5_id = response.json['data']['id']

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/award-complaint-reject.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, award_id, complaint2_id),
                {'data': {'status': 'invalid'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-accept.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, award_id, complaint1_id), {'data': {'status': 'accepted'}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, award_id, complaint3_id), {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, award_id, complaint4_id), {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, award_id, complaint5_id), {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-resolution-upload.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
                self.tender_id, award_id, complaint1_id),
                upload_files=[('file', u'ComplaintResolution.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-resolve.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, award_id, complaint1_id),
                {'data': {'status': 'satisfied'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-decline.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, award_id, complaint3_id),
                {'data': {'status': 'declined'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-accepted-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, award_id, complaint5_id), {'data': {'decision': 'Тендер скасовується замовником',
                                                                    'status': 'stopped'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaints-list.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, award_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, award_id, complaint1_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/award-complaint-accepted-stopping.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_id, complaint4_id, complaint4_token),
                {'data': {'cancellationReason': 'Тендер скасовується замовником', 'status': 'stopping'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('reviewer', ''))
        with open('docs/source/tutorial/award-complaint-stopping-stopped.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, award_id, complaint4_id),
                {'data': {'decision': 'Тендер скасовується замовником', 'status': 'stopped'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/award-complaint-satisfied-resolving.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
                self.tender_id, award_id, owner_token), {'data': {'status': 'cancelled'}})
            self.assertEqual(response.status, '200 OK')
            new_award_id = response.headers['Location'][-32:]

        with open('docs/source/tutorial/award-complaint-resolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_id, complaint1_id, owner_token),
                {'data': {'tendererAction': 'Умови виправлено, вибір переможня буде розгянуто повторно',
                          'status': 'resolved'}})
            self.assertEqual(response.status, '200 OK')



        self.app.authorization = ('Basic', ('broker', ''))
        award_id = new_award_id
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                            {'data': {'status': 'active'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/award-complaint-submit.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format
                                          (self.tender_id, award_id, bid_token),
                                          complaint)
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/award-complaint-cancel.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_id, response.json['data']['id'], response.json['access']['token']),
                {'data': {'cancellationReason': 'Умови виправлено', 'status': 'cancelled'}})
            self.assertEqual(response.status, '200 OK')


class TenderResourceTestStage2UA(BaseCompetitiveDialogUAStage2WebTest):
    docservice = True
    initial_data = test_tender_data_stage1

    def setUp(self):
        self.app = DumpsTestAppwebtest("config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()
            self.app.app.registry.docservice_url = 'http://public.docs-sandbox.openprocurement.org'

    def generate_docservice_url(self):
        return super(TenderResourceTestStage2UA,self).generate_docservice_url().replace(
            '/localhost/', '/public.docs-sandbox.openprocurement.org/'
        )

    def test_stage2_UA(self):
        request_path = '/tenders?opt_pretty=1'

        #### Exploring basic rules
        #

        self.app.authorization = ('Basic', ('competitive_dialogue', ''))

        test_tender_data_stage2UA['dialogue_token'] = sha512("super_secret_token").hexdigest()
        response = self.app.post_json('/tenders?opt_pretty=1', {"data": test_tender_data_stage2UA})
        self.assertEqual(response.status, '201 Created')
        self.tender_id = response.json['data']['id']
        tender = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                       {'data': {'status': 'draft.stage2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'draft.stage2')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender
        #

        tenderPeriod_endDate = get_now() + timedelta(days=30, seconds=10)
        with open('docs/source/tutorial/stage2/UA/patch-tender-periods.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}}})

        with open('docs/source/tutorial/stage2/UA/tender-activate.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': {'status': 'active.tendering'}})

        with open('docs/source/tutorial/stage2/UA/tender-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))


        #### Uploading documentation
        #

        with open('docs/source/tutorial/stage2/UA/upload-tender-notice.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'Notice.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]
        with open('docs/source/tutorial/stage2/UA/tender-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/upload-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token),
                                     upload_files=[('file', u'AwardCriteria.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        doc_id = response.json["data"]["id"]

        with open('docs/source/tutorial/stage2/UA/tender-documents-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents?acc_token={}'.format(self.tender_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/update-award-criteria.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/documents/{}?acc_token={}'.format(self.tender_id, doc_id, owner_token),
                                    upload_files=[('file', 'AwardCriteria-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/tender-documents-3.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/documents'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        #### Enquiries
        #

        with open('docs/source/tutorial/stage2/UA/ask-question-bad-participant.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                          question_with_bad_participant,
                                          status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/stage2/UA/ask-question.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(
                self.tender_id), question, status=201)
            question_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/UA/answer-question.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(
                self.tender_id, question_id, owner_token), answer, status=200)
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/list-question.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/get-answer.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question_id))
            self.assertEqual(response.status, '200 OK')

        self.go_to_enquiryPeriod_end()
        self.app.authorization = ('Basic', ('broker', ''))
        endDate = (get_now() + timedelta(days=30, seconds=10)).isoformat()
        with open('docs/source/tutorial/stage2/UA/update-tender-after-enqiery.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {'items': [{'deliveryDate': {'endDate': endDate}}]}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/stage2/UA/ask-question-after-enquiry-period.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), question, status=403)
            self.assertEqual(response.status, '403 Forbidden')

        with open('docs/source/tutorial/stage2/UA/update-tender-after-enqiery-with-update-periods.http', 'w') as self.app.file_obj:
            tenderPeriod_endDate = get_now() + timedelta(days=8)
            response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {
                                               'items': [{'deliveryDate': {'endDate': endDate}}],
                                               'tenderPeriod': {'endDate': tenderPeriod_endDate.isoformat()}
                                           }})
            self.assertEqual(response.status, '200 OK')


        #### Registering bid
        #

        bids_access = {}

        with open('docs/source/tutorial/stage2/UA/try-register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid_with_bad_participant,
                                          status=403)

        with open('docs/source/tutorial/stage2/UA/register-bidder.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid_stage2)
            bid1_id = response.json['data']['id']
            bids_access[bid1_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/UA/activate-bidder.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        #### Proposal Uploading
        #

        with open('docs/source/tutorial/stage2/UA/upload-bid-proposal.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]), upload_files=[('file', 'Proposal.pdf', 'content')])
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/UA/bidder-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')
        # make bids invalid
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                           {'data': {"value": {'amount': 501.0}}})
        self.assertEqual(response.status, '200 OK')

        #### Bid invalidation
        #

        with open('docs/source/tutorial/stage2/UA/bidder-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(
                self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        #### Bid confirmation
        #

        with open('docs/source/tutorial/stage2/UA/bidder-activate-after-changing-tender.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
                    self.tender_id, bid1_id, bids_access[bid1_id]), {'data': {'status': 'active'}})
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/register-2nd-bidder.http', 'w') as self.app.file_obj:
            for document in bid2_with_docs['data']['documents']:
                document['url'] = self.generate_docservice_url()
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), bid2_with_docs)
            bid2_id = response.json['data']['id']
            bids_access[bid2_id] = response.json['access']['token']
            self.assertEqual(response.status, '201 Created')


        #### Auction
        #
        self.set_status('active.auction')
        self.app.authorization = ('Basic', ('auction', ''))
        patch_data = {
            'auctionUrl': u'http://auction-sandbox.openprocurement.org/tenders/{}'.format(self.tender_id),
            'bids': [
                {
                    "id": bid1_id,
                    "participationUrl": u'http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}'.format(self.tender_id, bid1_id)
                },
                {
                    "id": bid2_id,
                    "participationUrl": u'http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}'.format(self.tender_id, bid2_id)
                }
            ]
        }
        response = self.app.patch_json('/tenders/{}/auction?acc_token={}'.format(self.tender_id, owner_token),
                                           {'data': patch_data})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/stage2/UA/auction-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/bidder-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid1_id, bids_access[bid1_id]))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/bidder2-participation-url.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid2_id, bids_access[bid2_id]))
            self.assertEqual(response.status, '200 OK')

        #### Confirming qualification
        #
        # self.set_status('active.qualification')
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                      {'data': {'bids': auction_bids_data}})

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        with open('docs/source/tutorial/stage2/UA/confirm-qualification.http', 'w') as self.app.file_obj:
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
                                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))
        self.contract_id = response.json['data'][0]['id']

        ####  Set contract value

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        with open('docs/source/tutorial/stage2/UA/tender-contract-set-contract-value.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), {'data': {'value': {'amount': 238}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 238)

        #### Setting contract signature date
        #

        with open('docs/source/tutorial/stage2/UA/tender-contract-sign-date.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), {'data': {"dateSigned": get_now().isoformat()} })
            self.assertEqual(response.status, '200 OK')

        #### Setting contract period

        period_dates = {"period": {"startDate": (get_now()).isoformat(), "endDate": (get_now() + timedelta(days=365)).isoformat()}}
        with open('docs/source/tutorial/stage2/UA/tender-contract-period.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token), {'data': {'period': period_dates["period"]}})
        self.assertEqual(response.status, '200 OK')

        #### Uploading contract documentation
        #

        with open('docs/source/tutorial/stage2/UA/tender-contract-upload-document.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/contracts/{}/documents?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token),
                upload_files=[('file', 'contract_document.doc', 'content')])
            self.assertEqual(response.status, '201 Created')
            self.document_id = response.json['data']['id']

        with open('docs/source/tutorial/stage2/UA/tender-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        #### Preparing the cancellation request
        #

        with open('docs/source/tutorial/stage2/UA/prepare-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
                    self.tender_id, owner_token), cancellation)
            self.assertEqual(response.status, '201 Created')

        cancellation_id = response.json['data']['id']

        with open('docs/source/tutorial/stage2/UA/update-cancellation-reasonType.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data": {'reasonType': 'unsuccessful'}})
            self.assertEqual(response.status, '200 OK')

        #### Filling cancellation with protocol and supplementary documentation
        #

        with open('docs/source/tutorial/stage2/UA/upload-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), upload_files=[('file', u'Notice.pdf', 'content')])
            cancellation_doc_id = response.json['data']['id']
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/tutorial/stage2/UA/patch-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                {'data': {"description": 'Changed description'}} )
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/stage2/UA/update-cancellation-doc.http', 'w') as self.app.file_obj:
            response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
                self.tender_id, cancellation_id, cancellation_doc_id, owner_token),
                upload_files=[('file', 'Notice-2.pdf', 'content2')])
            self.assertEqual(response.status, '200 OK')

        #### Activating the request and cancelling tender
        #

        with open('docs/source/tutorial/active-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
                    self.tender_id, cancellation_id, owner_token), {"data": {"status": "active"}})
            self.assertEqual(response.status, '200 OK')