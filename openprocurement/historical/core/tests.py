# -*- coding: utf-8 -*-
import unittest
from pyramid import testing
from pyramid.testing import DummyRequest
from jsonpointer import resolve_pointer
from openprocurement.historical.core import (
    HEADER,
    extract_header,
    add_header,
    apply_while
)

test_data_with_revisions = {
   "id": "0000eddc5df34fd6a20dca07f3081844",
   "procurementMethod": "limited",
   "status": "cancelled",
   "title_en": "[TESTING] Centralized web-enabled synergy",
   "description_en": "Eaque ipsa ut ipsam tempore saepe distinctio explicabo odit magnam est assumenda culpa ratione.",
   "procurementMethodType": "negotiation",
   "procuringEntity": {
       "contactPoint": {
           "url": "http://www.shev.gov.ua/",
           "email": "buh510@ukr.net",
           "telephone": "2341170",
           "name": "Ліповець Євген Іванович",
           "faxNumber": "2343591"
       },
       "identifier": {
           "scheme": "UA-EDR",
           "id": "37405111",
           "legalName": "Шевченківська районна в місті Києві державна адміністрація"
       },
       "name": "Шевченківська районна в місті Києві державна адміністрація",
       "kind": "general",
       "address": {
           "postalCode": "01030",
           "countryName": "Україна",
           "streetAddress": "Богдана Хмельницького вулиця, 21-29",
           "region": "Київська область",
           "locality": "Переяслав-Хмельницький"
       }
   },
   "revisions": [
       {
           "date": "2016-06-25T13:00:46.308399+03:00",
           "changes": [
               {
                   "path": "/procurementMethod",
                   "op": "remove"
               },
               {
                   "path": "/value",
                   "op": "remove"
               },
               {
                   "path": "/procurementMethodType",
                   "op": "remove"
               },
               {
                   "path": "/cause",
                   "op": "remove"
               },
               {
                   "path": "/description",
                   "op": "remove"
               },
               {
                   "path": "/title",
                   "op": "remove"
               },
               {
                   "path": "/items",
                   "op": "remove"
               },
               {
                   "path": "/title_en",
                   "op": "remove"
               },
               {
                   "path": "/description_en",
                   "op": "remove"
               },
               {
                   "path": "/status",
                   "op": "remove"
               },
               {
                   "path": "/tenderID",
                   "op": "remove"
               },
               {
                   "path": "/title_ru",
                   "op": "remove"
               },
               {
                   "path": "/id",
                   "op": "remove"
               },
               {
                   "path": "/procuringEntity",
                   "op": "remove"
               }
           ],
           "public": True,
           "author": "test.quintagroup.com"
       },
       {
           "date": "2016-06-25T13:02:22.103350+03:00",
           "changes": [
               {
                   "path": "/cancellations",
                   "op": "remove"
               }
           ],
           "rev": "1-ceaed033659c2b1237d393fda6233037",
           "public": True,
           "author": "test.quintagroup.com"
       },
       {
           "date": "2016-06-25T13:02:29.360395+03:00",
           "changes": [
               {
                   "path": "/cancellations/0/documents",
                   "op": "remove"
               }
           ],
           "rev": "2-909f500147c5c6d6ed16357fcee10f8b",
           "public": True,
           "author": "test.quintagroup.com"
       },
       {
           "date": "2016-06-25T13:02:31.418447+03:00",
           "changes": [
               {
                   "path": "/cancellations/0/documents/0/description",
                   "op": "remove"
               }
           ],
           "rev": "3-00ddf59089c6539de4f856f3b4865dbb",
           "public": True,
           "author": "test.quintagroup.com"
       },
       {
           "date": "2016-06-25T13:02:33.944422+03:00",
           "changes": [
               {
                   "path": "/cancellations/0/status",
                   "value": "pending",
                   "op": "replace"
               },
               {
                   "path": "/status",
                   "value": "active",
                   "op": "replace"
               }
           ],
           "rev": "4-744062ec04a89d217dbf126cfc26840b",
           "public": True,
           "author": "test.quintagroup.com"
       }
   ],
   "title": "[ТЕСТУВАННЯ] Чортеня насупереки зціліти люб'ячий.",
   "cause": "stateLegalServices",
   "description": "Шолупайка розжовувати победрина десяточок кукіль гаріль мужичий таляровий райдуга.",
   "cancellations": [
       {
           "status": "active",
           "documents": [
               {
                   "description": "Борозний утинок зморхтися чуркати ураз II постогнувати хрокнути гармашний надкусити чортеня потріпки.",
                   "title": "/tmp/d-5012267fomnisvzjrZZ.pdf",
                   "url": "https://public.docs-sandbox.openprocurement.org/get/8e4dbf87ef384bf08bc66f1f5d2a3457?Prefix=0000eddc5df34fd6a20dca07f3081844%2F1da6291722e84c7bb6dc9767a1821d79&KeyID=1331dc52&Signature=yU7zw6veH2sqWeN6N60dt6iVus0ctx0A4gyDo0bVMwwU1LxzAQwWYctpxoe0Brm3VvD%2FCnvUdmcqJgR2M6hcDQ%253D%253D",
                   "format": "application/pdf",
                   "documentOf": "tender",
                   "datePublished": "2016-06-25T13:02:29.303255+03:00",
                   "id": "1da6291722e84c7bb6dc9767a1821d79",
                   "dateModified": "2016-06-25T13:02:29.303281+03:00"
               }
           ],
           "reason": "Матюнка обгравати суддя прокадити зажати чужоземець пообскрібати нечулий клямати стругнути зближати муркотати накрашувати атака.",
           "reasonType": "cancelled",
           "date": "2016-06-25T13:02:22.102092+03:00",
           "cancellationOf": "tender",
           "id": "09e0316ed37741519fca65426be78bec"
       }
   ],
   "value": {
       "currency": "UAH",
       "amount": 89822995386.57,
       "valueAddedTaxIncluded": True
   },
   "tenderID": "UA-2016-06-25-000047",
   "title_ru": "[ТЕСТИРОВАНИЕ] Grass-roots empowering neural-net",
   "items": [
       {
           "description": "i-c0a27c73: Клей СМ-11",
           "classification": {
               "scheme": "CPV",
               "description": "Клеї",
               "id": "24910000-6"
           },
           "description_en": "Glue SM-11",
           "additionalClassifications": [
               {
                   "scheme": "ДКПП",
                   "id": "20.52.10-80.00",
                   "description": "Клеї готові та інші готові адгезиви, н.в.і.у."
               }
           ],
           "deliveryLocation": {
               "latitude": 50.537702,
               "longitude": 30.174488
           },
           "deliveryAddress": {
               "locality": "Ворзель",
               "region": "Київська область",
               "countryName_en": "Ukraine",
               "countryName": "Україна",
               "streetAddress": "вулиця Курортна, 22",
               "countryName_ru": "Украина",
               "postalCode": "08296"
           },
           "deliveryDate": {
               "endDate": "2016-07-10T13:00:42.021318+03:00"
           },
           "description_ru": "Клей СМ-11",
           "id": "6e1f8532aabd486fa25b79321cae502e",
           "unit": {
               "code": "KGM",
               "name": "килограммы"
           },
           "quantity": 51
       },
       {
           "description": "i-21178d07: Клей СМ-11",
           "classification": {
               "scheme": "CPV",
               "description": "Клеї",
               "id": "24910000-6"
           },
           "description_en": "Glue SM-11",
           "additionalClassifications": [
               {
                   "scheme": "ДКПП",
                   "id": "20.52.10-80.00",
                   "description": "Клеї готові та інші готові адгезиви, н.в.і.у."
               }
           ],
           "deliveryLocation": {
               "latitude": 48.465356,
               "longitude": 35.045667
           },
           "deliveryAddress": {
               "locality": "Дніпропетровськ",
               "region": "Дніпропетровська область",
               "countryName_en": "Ukraine",
               "countryName": "Україна",
               "streetAddress": "проспект Карла Маркса, 52",
               "countryName_ru": "Украина",
               "postalCode": "50064"
           },
           "deliveryDate": {
               "endDate": "2016-07-10T13:00:42.023585+03:00"
           },
           "description_ru": "Клей СМ-11",
           "id": "a216757d48e7428cb98c537d6e4eb714",
           "unit": {
               "code": "KGM",
               "name": "килограммы"
           },
           "quantity": 48
       }
   ],
   "dateModified": "2016-06-25T13:02:33.944499+03:00",

} 


class HistoricalTest(unittest.TestCase):

    def test_extract_header_invalid(self):
        for header in ["1.1", "-1", "-1.5", "", "asd"]:
            request = DummyRequest(headers={HEADER: header})
            self.assertFalse(extract_header(request, HEADER))

    def test_extract_header_valid(self):
        for header in ["1", "2", "0"]:
            request = DummyRequest(headers={HEADER: header})
            self.assertEqual(int(header), extract_header(request, HEADER))

    def test_add_header_str(self):
        request = DummyRequest()
        add_header(request, 'test-header', HEADER)
        self.assertIn(HEADER, request.response.headers)
        self.assertEqual('test-header', request.response.headers[HEADER])

    def test_add_header_int(self):
        request = DummyRequest()
        add_header(request, 42, HEADER)
        self.assertIn(HEADER, request.response.headers)
        self.assertEqual('42', request.response.headers[HEADER])

    def test_apply_while(self):
        doc = test_data_with_revisions.copy()
        del doc['revisions']
        revisions = test_data_with_revisions['revisions']
        for rev in reversed(revisions[1:]):
            patched = apply_while(doc, revisions, rev['rev'])
            for ch in rev['changes']:
                if ch['op'] != 'remove':
                    val = resolve_pointer(patched, ch['path'])
                    self.assertEqual(ch['value'], val)
                else:
                    self.assertEqual(
                        resolve_pointer(patched, ch['path'], 'missing'),
                        'missing')
