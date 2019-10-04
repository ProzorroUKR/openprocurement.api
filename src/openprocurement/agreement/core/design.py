# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition
from openprocurement.api import design


FIELDS = ["agreementID"]
CHANGES_FIELDS = FIELDS + ["dateModified"]


def add_design():
    for i, j in globals().items():
        if "_view" in i:
            setattr(design, i, j)


agreements_all_view = ViewDefinition(
    "agreements",
    "all",
    """function(doc) {
    if(doc.doc_type == 'Agreement') {
        emit(doc.agreementID, null);
    }
}""",
)


agreements_by_dateModified_view = ViewDefinition(
    "agreements",
    "by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Agreement') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % FIELDS,
)

agreements_real_by_dateModified_view = ViewDefinition(
    "agreements",
    "real_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Agreement' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % FIELDS,
)

agreements_test_by_dateModified_view = ViewDefinition(
    "agreements",
    "test_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Agreement' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % FIELDS,
)

agreements_by_local_seq_view = ViewDefinition(
    "agreements",
    "by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Agreement') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % CHANGES_FIELDS,
)

agreements_real_by_local_seq_view = ViewDefinition(
    "agreements",
    "real_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Agreement' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % CHANGES_FIELDS,
)

agreements_test_by_local_seq_view = ViewDefinition(
    "agreements",
    "test_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Agreement' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % CHANGES_FIELDS,
)

conflicts_view = ViewDefinition(
    "conflicts",
    "all",
    """function(doc) {
    if (doc._conflicts) {
        emit(doc._rev, [doc._rev].concat(doc._conflicts));
    }
}""",
)
