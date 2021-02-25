# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition

from openprocurement.api import design

FRAMEWORK_FIELDS = [
    "id",
    "title",
    "prettyID",
    "enquiryPeriod",
    "period",
    "qualificationPeriod",
    "status",
    "frameworkType",
    "next_check",
]
FRAMEWORK_CHANGES_FIELDS = FRAMEWORK_FIELDS + ["dateModified"]


SUBMISSION_FIELDS = [
    "id",
    "frameworkID",
    "qualificationID",
    "status",
    "tenderers",
    "documents",
    "date",
    "datePublished",
]

SUBMISSION_CHANGES_FIELDS = SUBMISSION_FIELDS + ["dateModified"]

QUALIFICATION_FIELDS = [
    "id",
    "frameworkID",
    "submissionID",
    "status",
    "documents",
    "date",
]

QUALIFICATION_CHANGES_FIELDS = QUALIFICATION_FIELDS + ["dateModified"]

AGREEMENT_FIELDS = [
    "id",
    "agreementID",
    "agreementType",
    "status",
    "tender_id",
    "next_check",
]
AGREEMENT_CHANGES_FIELDS = AGREEMENT_FIELDS + ["dateModified"]


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
    % FRAMEWORK_FIELDS,
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
    % FRAMEWORK_FIELDS,
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
    % FRAMEWORK_FIELDS,
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
    % FRAMEWORK_CHANGES_FIELDS,
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
    % FRAMEWORK_CHANGES_FIELDS,
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
    % FRAMEWORK_CHANGES_FIELDS,
)

# Submissions design

submissions_all_view = ViewDefinition(
    "submissions",
    "all",
    """function(doc) {
    if(doc.doc_type == 'Submission') {
        emit(doc._id, null);
    }
}""",
)


submissions_by_dateModified_view = ViewDefinition(
    "submissions",
    "by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Submission' && doc.status != 'draft' && doc.status != 'deleted') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % SUBMISSION_FIELDS,
)

submissions_real_by_dateModified_view = ViewDefinition(
    "submissions",
    "real_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Submission' && doc.status != 'draft' && doc.status != 'deleted' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % SUBMISSION_FIELDS,
)

submissions_test_by_dateModified_view = ViewDefinition(
    "submissions",
    "test_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Submission' && doc.status != 'draft' && doc.status != 'deleted' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % SUBMISSION_FIELDS,
)

submissions_by_local_seq_view = ViewDefinition(
    "submissions",
    "by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Submission' && doc.status != 'draft' && doc.status != 'deleted') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % SUBMISSION_CHANGES_FIELDS,
)

submissions_real_by_local_seq_view = ViewDefinition(
    "submissions",
    "real_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Submission' && doc.status != 'draft' && doc.status != 'deleted' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % SUBMISSION_CHANGES_FIELDS,
)

submissions_test_by_local_seq_view = ViewDefinition(
    "submissions",
    "test_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Submission' && doc.status != 'draft' && doc.status != 'deleted' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % SUBMISSION_CHANGES_FIELDS,
)

submissions_by_framework_id_view = ViewDefinition(
    'submissions',
    'by_framework_id', '''function(doc) {
    if(doc.doc_type == 'Submission' && doc.status != 'draft' && doc.status != 'deleted') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit([doc.frameworkID, doc.dateModified], data);
    }
}''' % SUBMISSION_CHANGES_FIELDS)

submissions_by_framework_id_total_view = ViewDefinition(
    submissions_by_framework_id_view.design,
    submissions_by_framework_id_view.name + "_total",
    submissions_by_framework_id_view.map_fun,
    "_count"
)

submissions_active_by_framework_id_count_view = ViewDefinition(
    "submissions",
    "active_by_framework_id",
    '''function(doc) {
        if(doc.doc_type == 'Submission' && doc.status == 'active') {
            emit([doc.frameworkID, doc.tenderers[0].identifier.id], doc._id);
        }
    }''',
    "_count",
)

# Qualification design

qualifications_all_view = ViewDefinition(
    "qualifications",
    "all",
    """function(doc) {
    if(doc.doc_type == 'Qualification') {
        emit(doc._id, null);
    }
}""",
)


qualifications_by_dateModified_view = ViewDefinition(
    "qualifications",
    "by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Qualification' && doc.status != 'draft') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % QUALIFICATION_FIELDS,
)

qualifications_real_by_dateModified_view = ViewDefinition(
    "qualifications",
    "real_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Qualification' && doc.status != 'draft' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % QUALIFICATION_FIELDS,
)

qualifications_test_by_dateModified_view = ViewDefinition(
    "qualifications",
    "test_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Qualification' && doc.status != 'draft' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc.dateModified, data);
    }
}"""
    % QUALIFICATION_FIELDS,
)

qualifications_by_local_seq_view = ViewDefinition(
    "qualifications",
    "by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Qualification' && doc.status != 'draft') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % QUALIFICATION_CHANGES_FIELDS,
)

qualifications_real_by_local_seq_view = ViewDefinition(
    "qualifications",
    "real_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Qualification' && doc.status != 'draft' && !doc.mode) {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % QUALIFICATION_CHANGES_FIELDS,
)

qualifications_test_by_local_seq_view = ViewDefinition(
    "qualifications",
    "test_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Qualification' && doc.status != 'draft' && doc.mode == 'test') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit(doc._local_seq, data);
    }
}"""
    % QUALIFICATION_CHANGES_FIELDS,
)

qualifications_by_framework_id_view = ViewDefinition(
    'qualifications',
    'by_framework_id', '''function(doc) {
    if(doc.doc_type == 'Qualification' && doc.status != 'draft') {
        var fields=%s, data={};
        for (var i in fields) {
            if (doc[fields[i]]) {
                data[fields[i]] = doc[fields[i]]
            }
        }
        emit([doc.frameworkID, doc.dateModified], data);
    }
}''' % QUALIFICATION_CHANGES_FIELDS)

qualifications_by_framework_id_total_view = ViewDefinition(
    qualifications_by_framework_id_view.design,
    qualifications_by_framework_id_view.name + "_total",
    qualifications_by_framework_id_view.map_fun,
    "_count"
)

# Agreements design

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
    % AGREEMENT_FIELDS,
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
    % AGREEMENT_FIELDS,
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
    % AGREEMENT_FIELDS,
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
    % AGREEMENT_CHANGES_FIELDS,
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
    % AGREEMENT_CHANGES_FIELDS,
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
    % AGREEMENT_CHANGES_FIELDS,
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