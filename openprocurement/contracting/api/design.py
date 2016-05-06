# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition
from openprocurement.api import design


FIELDS = [
    'contractID',
]
CHANGES_FIELDS = FIELDS + [
    'dateModified',
]


def add_design():
    for i, j in globals().items():
        if "_view" in i:
            setattr(design, i, j)


contracts_all_view = ViewDefinition('contracts', 'all', '''function(doc) {
    if(doc.doc_type == 'Contract') {
        emit(doc.contractID, null);
    }
}''')


contracts_by_dateModified_view = ViewDefinition('contracts', 'by_dateModified', '''function(doc) {
    if(doc.doc_type == 'Contract' && doc.status != 'draft') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}''' % FIELDS)

contracts_real_by_dateModified_view = ViewDefinition('contracts', 'real_by_dateModified', '''function(doc) {
    if(doc.doc_type == 'Contract' && doc.status != 'draft' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}''' % FIELDS)

contracts_test_by_dateModified_view = ViewDefinition('contracts', 'test_by_dateModified', '''function(doc) {
    if(doc.doc_type == 'Contract' && doc.status != 'draft' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}''' % FIELDS)

contracts_by_local_seq_view = ViewDefinition('contracts', 'by_local_seq', '''function(doc) {
    if(doc.doc_type == 'Contract' && doc.status != 'draft') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}''' % CHANGES_FIELDS)

contracts_real_by_local_seq_view = ViewDefinition('contracts', 'real_by_local_seq', '''function(doc) {
    if(doc.doc_type == 'Contract' && doc.status != 'draft' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}''' % CHANGES_FIELDS)

contracts_test_by_local_seq_view = ViewDefinition('contracts', 'test_by_local_seq', '''function(doc) {
    if(doc.doc_type == 'Contract' && doc.status != 'draft' && doc.mode == 'test') {
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

