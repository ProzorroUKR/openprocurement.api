# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition
from couchdb import Server
from collections import defaultdict


# this object is supposed to contain all database views
# at the moment all packages assign views as attributes to this module that isn't obvious
VIEWS = defaultdict(list)


def add_index_options(doc):
    doc["options"] = {"local_seq": True}


def sync_design(db):
    views = [j for i, j in globals().items() if "_view" in i]
    ViewDefinition.sync_many(db, views, callback=add_index_options)


def sync_design_databases(server: Server, db_names: dict):
    # specific databases views
    for db_key, views in VIEWS.items():
        views.append(conflicts_view)  # should be in every db
        db_name = db_names[db_key]
        ViewDefinition.sync_many(server[db_name], views, callback=add_index_options)


conflicts_view = ViewDefinition(
    "conflicts",
    "all",
    """function(doc) {
    if (doc._conflicts) {
        emit(doc._rev, [doc._rev].concat(doc._conflicts));
    }
}""",
)
