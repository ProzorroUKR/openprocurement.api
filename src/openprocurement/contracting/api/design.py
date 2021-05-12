# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition
from openprocurement.api.database import Databases
from openprocurement.api.design import VIEWS


FIELDS = ["contractID"]
CHANGES_FIELDS = FIELDS + ["dateModified"]


def add_design():
    db_keys = Databases.keys()  # ("frameworks", "submissions", "plans", etc)
    for var_name, obj in globals().items():
        if isinstance(obj, ViewDefinition):
            db_key = var_name.split("_")[0]  # frameworks_bla_bla_bla = ViewDefinition(...
            # obj.design will be _design/frameworks, would be parsing it better ?
            assert db_key in db_keys, f"ViewDefinition must follow the name convention: {db_key}, {db_keys}"
            VIEWS[db_key].append(obj)


contracts_all_view = ViewDefinition(
    "contracts",
    "all",
    """function(doc) {
    if(doc.doc_type == 'Contract') {
        emit(doc.contractID, null);
    }
}""",
)


contracts_by_dateModified_view = ViewDefinition(
    "contracts",
    "by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Contract') {
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

contracts_real_by_dateModified_view = ViewDefinition(
    "contracts",
    "real_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Contract' && !doc.mode) {
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

contracts_test_by_dateModified_view = ViewDefinition(
    "contracts",
    "test_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Contract' && doc.mode == 'test') {
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

contracts_by_local_seq_view = ViewDefinition(
    "contracts",
    "by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Contract') {
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

contracts_real_by_local_seq_view = ViewDefinition(
    "contracts",
    "real_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Contract' && !doc.mode) {
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

contracts_test_by_local_seq_view = ViewDefinition(
    "contracts",
    "test_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Contract' && doc.mode == 'test') {
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
