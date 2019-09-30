# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition
from openprocurement.api import design


FIELDS = [
    'planID',
]
CHANGES_FIELDS = FIELDS + [
    'dateModified',
]


def add_design():
    for i, j in globals().items():
        if "_view" in i:
            setattr(design, i, j)


plans_all_view = ViewDefinition('plans', 'all', '''function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft') {
        emit(doc.planID, null);
    }
}''')


plans_by_dateModified_view = ViewDefinition('plans', 'by_dateModified', '''function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}''' % FIELDS)

plans_real_by_dateModified_view = ViewDefinition('plans', 'real_by_dateModified', '''function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}''' % FIELDS)

plans_test_by_dateModified_view = ViewDefinition('plans', 'test_by_dateModified', '''function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}''' % FIELDS)

plans_by_local_seq_view = ViewDefinition('plans', 'by_local_seq', '''function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}''' % CHANGES_FIELDS)

plans_real_by_local_seq_view = ViewDefinition('plans', 'real_by_local_seq', '''function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}''' % CHANGES_FIELDS)

plans_test_by_local_seq_view = ViewDefinition('plans', 'test_by_local_seq', '''function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}''' % CHANGES_FIELDS)

conflicts_view = ViewDefinition('conflicts', 'all', '''function(doc) {
    if (doc._conflicts) {
        emit(doc._rev, [doc._rev].concat(doc._conflicts));
    }
}''')
