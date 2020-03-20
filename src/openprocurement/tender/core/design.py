# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition
from openprocurement.api import design
from openprocurement.api.constants import RELEASE_2020_04_19

FIELDS = [
    "auctionPeriod",
    "status",
    "tenderID",
    "lots",
    "procurementMethodType",
    "next_check",
    #'auctionUrl',
    #'awardPeriod',
    #'dateModified',
    #'description',
    #'description_en',
    #'description_ru',
    #'enquiryPeriod',
    #'minimalStep',
    #'mode',
    #'procuringEntity',
    #'tenderPeriod',
    #'title',
    #'title_en',
    #'title_ru',
    #'value',
]
CHANGES_FIELDS = FIELDS + ["dateModified"]


def add_design():
    for i, j in globals().items():
        if "_view" in i:
            setattr(design, i, j)


tenders_all_view = ViewDefinition(
    "tenders",
    "all",
    """function(doc) {
    if(doc.doc_type == 'Tender') {
        emit(doc.tenderID, null);
    }
}""",
)


tenders_by_dateModified_view = ViewDefinition(
    "tenders",
    "by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Tender' && doc.status != 'draft') {
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

tenders_real_by_dateModified_view = ViewDefinition(
    "tenders",
    "real_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Tender' && doc.status != 'draft' && !doc.mode) {
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

tenders_test_by_dateModified_view = ViewDefinition(
    "tenders",
    "test_by_dateModified",
    """function(doc) {
    if(doc.doc_type == 'Tender' && doc.status != 'draft' && doc.mode == 'test') {
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

tenders_by_local_seq_view = ViewDefinition(
    "tenders",
    "by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Tender' && doc.status != 'draft') {
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

tenders_real_by_local_seq_view = ViewDefinition(
    "tenders",
    "real_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Tender' && doc.status != 'draft' && !doc.mode) {
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

tenders_test_by_local_seq_view = ViewDefinition(
    "tenders",
    "test_by_local_seq",
    """function(doc) {
    if(doc.doc_type == 'Tender' && doc.status != 'draft' && doc.mode == 'test') {
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


complaints_by_complaint_id_view = ViewDefinition(
    "complaints",
    "by_complaint_id",
    """function (doc) {
    if (doc.doc_type == 'Tender' & doc.revisions[0].date > '%s') {
        function emit_complaints(item, tender_id, item_type, item_id) {
            var complaints = item.complaints;
            if (complaints) {
                for (var complaint_index in complaints) {
                    var complaint = complaints[complaint_index];
                    if (complaint.type == 'complaint') {
                        var data = {params: {}, access: {}};
                        data.params.tender_id = tender_id;
                        data.params.item_type = item_type;
                        data.params.item_id = item_id;
                        data.params.complaint_id = complaint.id;
                        data.access.token = complaint.owner_token;
                        emit(complaint.complaintID.toLowerCase(), data);
                    }
                }
            }
        }
        
        emit_complaints(doc, doc._id, null, null)
        
        var types = ['qualifications', 'awards', 'cancellations'];

        for (var type_index in types) {
            var type = types[type_index];
            if (doc[type]) {
                var items = doc[type]
                for (var item_index in items) {
                    var item = items[item_index];
                    emit_complaints(item, doc._id, type, item.id);
                }
            }
        }
    }
}
""" % RELEASE_2020_04_19.isoformat()
)
