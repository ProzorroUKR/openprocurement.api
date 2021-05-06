from couchdb.design import ViewDefinition
from openprocurement.api.database import Databases
from openprocurement.api.design import VIEWS


FIELDS = ["planID"]
CHANGES_FIELDS = FIELDS + ["dateModified"]


def add_design():
    db_keys = Databases.keys()  # ("frameworks", "submissions", "plans", etc)
    for var_name, obj in globals().items():
        if isinstance(obj, ViewDefinition):
            db_key = var_name.split("_")[0]  # frameworks_bla_bla_bla = ViewDefinition(...
            # obj.design will be _design/frameworks, would be parsing it better ?
            assert db_key in db_keys, f"ViewDefinition must follow the name convention: {db_key}, {db_keys}"
            VIEWS[db_key].append(obj)


plans_all_view = ViewDefinition(
    "plans",
    "all",
    """function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft') {
        emit(doc.planID, null);
    }
}""",
)


plans_by_dateModified_view = ViewDefinition(
    "plans",
    "by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft') {
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

plans_real_by_dateModified_view = ViewDefinition(
    "plans",
    "real_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && !doc.mode) {
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

plans_test_by_dateModified_view = ViewDefinition(
    "plans",
    "test_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && doc.mode == 'test') {
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

plans_by_local_seq_view = ViewDefinition(
    "plans",
    "by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft') {
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

plans_real_by_local_seq_view = ViewDefinition(
    "plans",
    "real_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && !doc.mode) {
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

plans_test_by_local_seq_view = ViewDefinition(
    "plans",
    "test_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Plan' && doc.status != 'draft' && doc.mode == 'test') {
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
