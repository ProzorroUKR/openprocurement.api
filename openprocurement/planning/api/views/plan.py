# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    context_unpack,
    decrypt,
    encrypt,
    generate_id,
    json_view,
    set_ownership,
)
from openprocurement.planning.api.design import (
    FIELDS,
    plans_by_dateModified_view,
    plans_real_by_dateModified_view,
    plans_test_by_dateModified_view,
    plans_by_local_seq_view,
    plans_real_by_local_seq_view,
    plans_test_by_local_seq_view,
)
from openprocurement.planning.api.utils import (
    generate_plan_id,
    save_plan,
    plan_serialize,
    apply_patch,
    opresource,
)
from openprocurement.planning.api.validation import (
    validate_patch_plan_data,
    validate_plan_data,
)

LOGGER = getLogger(__name__)
VIEW_MAP = {
    u'': plans_real_by_dateModified_view,
    u'test': plans_test_by_dateModified_view,
    u'_all_': plans_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u'': plans_real_by_local_seq_view,
    u'test': plans_test_by_local_seq_view,
    u'_all_': plans_by_local_seq_view,
}
FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


@opresource(name='Plans',
            path='/plans',
            description="Planing http://ocds.open-contracting.org/standard/r/1__0__0/en/schema/reference/#planning")
class PlansResource(object):
    def __init__(self, request, context):
        self.request = request
        self.server = request.registry.couchdb_server
        self.db = request.registry.db
        self.server_id = request.registry.server_id

    @json_view(permission='view_plan')
    def get(self):
        """Plans List

        Get Plans List
        ----------------

        Example request to get plans list:

        .. sourcecode:: http

            GET /plans HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                        "id": "64e93250be76435397e8c992ed4214d1",
                        "dateModified": "2014-10-27T08:06:58.158Z"
                    }
                ]
            }

        """
        # http://wiki.apache.org/couchdb/HTTP_view_API#Querying_Options
        params = {}
        pparams = {}
        fields = self.request.params.get('opt_fields', '')
        if fields:
            params['opt_fields'] = fields
            pparams['opt_fields'] = fields
            fields = fields.split(',')
            view_fields = fields + ['dateModified', 'id']
        limit = self.request.params.get('limit', '')
        if limit:
            params['limit'] = limit
            pparams['limit'] = limit
        limit = int(limit) if limit.isdigit() and int(limit) > 0 else 100
        descending = bool(self.request.params.get('descending'))
        offset = self.request.params.get('offset', '')
        if descending:
            params['descending'] = 1
        else:
            pparams['descending'] = 1
        feed = self.request.params.get('feed', '')
        view_map = FEED.get(feed, VIEW_MAP)
        changes = view_map is CHANGES_VIEW_MAP
        if feed and feed in FEED:
            params['feed'] = feed
            pparams['feed'] = feed
        mode = self.request.params.get('mode', '')
        if mode and mode in view_map:
            params['mode'] = mode
            pparams['mode'] = mode
        view_limit = limit + 1 if offset else limit
        if changes:
            if offset:
                view_offset = decrypt(self.server.uuid, self.db.name, offset)
                if view_offset and view_offset.isdigit():
                    view_offset = int(view_offset)
                else:
                    self.request.errors.add('params', 'offset', 'Offset expired/invalid')
                    self.request.errors.status = 404
                    return
            if not offset:
                view_offset = 'now' if descending else 0
        else:
            if offset:
                view_offset = offset
            else:
                view_offset = '9' if descending else ''
        list_view = view_map.get(mode, view_map[u''])
        if fields:
            if not changes and set(fields).issubset(set(FIELDS)):
                results = [
                    (dict([(i, j) for i, j in x.value.items() + [('id', x.id), ('dateModified', x.key)] if
                           i in view_fields]), x.key)
                    for x in list_view(self.db, limit=view_limit, startkey=view_offset, descending=descending)
                    ]
            elif changes and set(fields).issubset(set(FIELDS)):
                results = [
                    (dict([(i, j) for i, j in x.value.items() + [('id', x.id)] if i in view_fields]), x.key)
                    for x in list_view(self.db, limit=view_limit, startkey=view_offset, descending=descending)
                    ]
            elif fields:
                LOGGER.info('Used custom fields for planss list: {}'.format(','.join(sorted(fields))),
                            extra=context_unpack(self.request, {'MESSAGE_ID': 'plan_list_custom'}))

                results = [
                    (plan_serialize(self.request, i[u'doc'], view_fields), i.key)
                    for i in
                    list_view(self.db, limit=view_limit, startkey=view_offset, descending=descending, include_docs=True)
                    ]
        else:
            results = [
                ({'id': i.id, 'dateModified': i.value['dateModified']} if changes else {'id': i.id,
                                                                                        'dateModified': i.key}, i.key)
                for i in list_view(self.db, limit=view_limit, startkey=view_offset, descending=descending)
                ]
        if results:
            params['offset'], pparams['offset'] = results[-1][1], results[0][1]
            if offset and view_offset == results[0][1]:
                results = results[1:]
            elif offset and view_offset != results[0][1]:
                results = results[:limit]
                params['offset'], pparams['offset'] = results[-1][1], view_offset
            results = [i[0] for i in results]
            if changes:
                params['offset'] = encrypt(self.server.uuid, self.db.name, params['offset'])
                pparams['offset'] = encrypt(self.server.uuid, self.db.name, pparams['offset'])
        else:
            params['offset'] = offset
            pparams['offset'] = offset
        data = {
            'data': results,
            'next_page': {
                "offset": params['offset'],
                "path": self.request.route_path('Plans', _query=params),
                "uri": self.request.route_url('Plans', _query=params)
            }
        }
        if descending or offset:
            data['prev_page'] = {
                "offset": pparams['offset'],
                "path": self.request.route_path('Plans', _query=pparams),
                "uri": self.request.route_url('Plans', _query=pparams)
            }
        return data

    @json_view(content_type="application/json", permission='create_plan', validators=(validate_plan_data,))
    def post(self):
        """This API request is targeted to creating new Plan by procuring organizations.

        Creating new Plan

        -------------------

        Example request to create plan:

        .. sourcecode:: http

            POST /plans HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "tender": {
                        "procurementMethod": "допорогові закупівлі",
                        "tenderPeriod": {
                            "startDate": "2015-05-09T23:11:39.720908+03:00"
                        }
                    },
                    "items": [
                        {
                            "deliveryDate": {
                                "endDate": "2015-05-11T23:11:39.721063+03:00"
                            },
                            "additionalClassifications": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "28.29.39-10.00",
                                    "description": "Прилади контролювання маси та прилади контрольні автоматичні з максимальною масою зважування не більше ніж 5000 кг"
                                }
                            ],
                            "unit": {
                                "code": "KGM",
                                "name": "кг"
                            },
                            "classification": {
                                "scheme": "CPV",
                                "description": "Роботи з будування пневматичних будівель",
                                "id": "45217000-1"
                            },
                            "quantity": 760
                        }
                    ],
                    "procuringEntity": {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Уравління Справами"
                        },
                        "name": "ДУС"
                    },
                    "budget": {
                        "project": {
                            "name": "proj_name",
                            "id": "proj_id"
                        },
                        "amount": 10000,
                        "amountNet": 12222,
                        "id": "budget_id",
                        "description": "budget_description"
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Location: http://localhost/api/0.10/plans/84582807b5654bee9e216adb05e57d39
            Content-Type: application/json

            {
                "access": {
                    "token": "e4c75de4320649a4bbbdfa180e7a9ef2"
                },
                "data": {
                    "items": [
                        {
                            "classification": {
                                "scheme": "CPV",
                                "description": "Роботи з будування пневматичних будівель",
                                "id": "45217000-1"
                            },
                            "additionalClassifications": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "28.29.39-10.00",
                                    "description": "Прилади контролювання маси та прилади контрольні"
                                },
                                {
                                    "scheme": "КЕКВ",
                                    "id": "123",
                                    "description": "-"
                                }
                            ],
                            "deliveryDate": {
                                "endDate": "2015-05-11T23:11:39.721063+03:00"
                            },
                            "id": "8cd4abfd0bbb489a83a81dec1393ab8d",
                            "unit": {
                                "code": "KGM",
                                "name": "кг"
                            },
                            "quantity": 760
                        }
                    ],
                    "planID": "UA-2015-11-26-000001",
                    "budget": {
                        "amountNet": 12222,
                        "description": "budget_description",
                        "project": {
                            "id": "proj_id",
                            "name": "proj_name"
                        },
                        "currency": "UAH",
                        "amount": 10000,
                        "id": "budget_id"
                    },
                    "procuringEntity": {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Уравління Справами"
                        },
                        "name": "ДУС"
                    },
                    "tender": {
                        "procurementMethod": "open",
                        "tenderPeriod": {
                            "startDate": "2015-05-09T23:11:39.720908+03:00"
                        }
                    },
                    "id": "ac658c4ff7ab47dea27e32d15a655ddb"
                }
}
        """
        plan_id = generate_id()
        plan = self.request.validated['plan']
        plan.id = plan_id

        plan.planID = generate_plan_id(get_now(), self.db, self.server_id)
        set_ownership(plan, self.request)
        self.request.validated['plan'] = plan
        self.request.validated['plan_src'] = {}
        if save_plan(self.request):
            LOGGER.info('Created plan {} ({})'.format(plan_id, plan.planID),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'plan_create'},
                                             {'plan_id': plan_id, 'planID': plan.planID}))
            self.request.response.status = 201
            self.request.response.headers[
                'Location'] = self.request.route_url('Plan', plan_id=plan_id)
            return {
                'data': plan.serialize("view"),
                'access': {
                    'token': plan.owner_token
                }
            }


@opresource(name='Plan',
            path='/plans/{plan_id}',
            description="Planing http://ocds.open-contracting.org/standard/r/1__0__0/en/schema/reference/#planning")
class PlanResource(object):
    def __init__(self, request, context):
        self.request = request
        self.db = request.registry.db

    @json_view(permission='view_plan')
    def get(self):
        """Plan Read


        Get Plan
        ----------

        Example request to get tender:

        .. sourcecode:: http

            GET /plans/62179f8f94a246239268750a6eb0e53f HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "items": [
                        {
                            "classification": {
                                "scheme": "CPV",
                                "description": "Роботи з будування пневматичних будівель",
                                "id": "45217000-1"
                            },
                            "additionalClassifications": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "28.29.39-10.00",
                                    "description": "Прилади контролювання маси та прилади контрольні автоматичні з максимальною масою зважування не більше ніж 5000 кг"
                                }
                            ],
                            "deliveryDate": {
                                "endDate": "2015-05-11T23:11:39.721063+03:00"
                            },
                            "id": "62179f8f94a246239268750a6eb0e53f",
                            "unit": {
                                "code": "KGM",
                                "name": "кг"
                            },
                            "quantity": 760
                        }
                    ],
                    "planID": "UA-2015-11-16-000001",
                    "budget": {
                        "project": {
                            "id": "proj_id",
                            "name": "proj_name"
                        },
                        "amount": 10000,
                        "amountNet": 12222,
                        "id": "budget_id",
                        "description": "budget_description"
                    },
                    "id": "9b07a65c921e47e7ab3fb9eafb3f44a5",
                    "procuringEntity": {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Уравління Справами"
                        },
                        "name": "ДУС"
                    },
                    "tender": {
                        "procurementMethod": "допорогові закупівлі",
                        "tenderPeriod": {
                            "startDate": "2015-05-09T23:11:39.720908+03:00"
                        }
                    },
                    "dateModified": "2015-11-16T16:33:02.915600+02:00"
                }
            }

        """
        plan = self.request.validated['plan']
        plan_data = plan.serialize('view')
        return {'data': plan_data}

    @json_view(content_type="application/json", validators=(validate_patch_plan_data,), permission='edit_plan')
    def patch(self):
        """Plan Edit (partial)

        For example here is how procuring entity can change name:

        .. sourcecode:: http

            PATCH /plans/62179f8f94a246239268750a6eb0e53f HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "procuringEntity": {
                        "identifier": {
                            "legalName": "ДП Державне Уравління Справами11"
                        },
                        "name": "ДУС"
                    },
                    "budget": {
                        "project": {
                            "name": "proj_name",
                            "id": "proj_id"
                        },
                        "amount": 10020,
                        "amountNet": 22222,
                        "id": "budget_id",
                        "description": "budget_description"
                    }
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

        """
        plan = self.request.validated['plan']

        data = self.request.validated['data']
        apply_patch(self.request, src=self.request.validated['plan_src'])
        LOGGER.info('Updated plan {}'.format(plan.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'plan_patch'}))
        return {'data': plan.serialize('view')}
