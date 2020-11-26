# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition

from openprocurement.api import design

FIELDS = ["id",
          "prettyID",
          "enquiryPeriod",
          "period",
          "qualificationPeriod",
          "status",
          "frameworkType",
          "next_check",
          ]
CHANGES_FIELDS = FIELDS + ["dateModified"]


def add_design():
    for i, j in globals().items():
        if "_view" in i:
            setattr(design, i, j)


frameworks_all_view = ViewDefinition(
    "frameworks",
    "all",
    """function(doc) {
    if(doc.doc_type == 'Framework') {
        emit(doc.prettyID, null);
    }
}""",
)


frameworks_by_dateModified_view = ViewDefinition(
    "frameworks",
    "by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Framework' && doc.status != 'draft') {
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

frameworks_real_by_dateModified_view = ViewDefinition(
    "frameworks",
    "real_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Framework' && doc.status != 'draft' && !doc.mode) {
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

frameworks_test_by_dateModified_view = ViewDefinition(
    "frameworks",
    "test_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Framework' && doc.status != 'draft' && doc.mode == 'test') {
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

frameworks_by_local_seq_view = ViewDefinition(
    "frameworks",
    "by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Framework' && doc.status != 'draft') {
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

frameworks_real_by_local_seq_view = ViewDefinition(
    "frameworks",
    "real_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Framework' && doc.status != 'draft' && !doc.mode) {
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

frameworks_test_by_local_seq_view = ViewDefinition(
    "frameworks",
    "test_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Framework' && doc.status != 'draft' && doc.mode == 'test') {
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
