import argparse
import os
from uuid import uuid4
from pbkdf2 import PBKDF2
from configparser import ConfigParser
from couchdb import Server as CouchdbServer, Session, Database
from couchdb.http import Unauthorized, extract_credentials
from openprocurement.api.design import sync_design, sync_design_databases
from logging import getLogger
from dataclasses import dataclass, fields
from pymongo import MongoClient, ReturnDocument, DESCENDING, ASCENDING, ReadPreference
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from bson.codec_options import TypeRegistry
from bson.codec_options import CodecOptions
from bson.decimal128 import Decimal128
from decimal import Decimal
from datetime import datetime, timezone

LOGGER = getLogger("{}.init".format(__name__))

SECURITY = {"admins": {"names": [], "roles": ["_admin"]}, "members": {"names": [], "roles": ["_admin"]}}
VALIDATE_DOC_ID = "_design/_auth"
VALIDATE_DOC_UPDATE = """function(newDoc, oldDoc, userCtx){
    if(newDoc._deleted && newDoc.tenderID) {
        throw({forbidden: 'Not authorized to delete this document'});
    }
    if(userCtx.roles.indexOf('_admin') !== -1) {
        return;
    }
    if(userCtx.name === '%s') {
        return;
    } else {
        throw({forbidden: 'Only authorized user may edit the database'});
    }
}"""


class Server(CouchdbServer):
    _uuid = None

    @property
    def uuid(self):
        """The uuid of the server.

        :rtype: basestring
        """
        if self._uuid is None:
            _, _, data = self.resource.get_json()
            self._uuid = data["uuid"]
        return self._uuid


@dataclass(init=False, eq=False)
class Databases:
    """
    Describes a global object to work with databases
    For ex `registry.databases.plans.get(uuid)`
    or `for db in registry.databases:`
    """
    migrations: Database
    frameworks: Database
    submissions: Database
    qualifications: Database
    agreements: Database

    transfers: Database

    plans: Database
    contracts: Database

    names: dict

    def __init__(self, admin_connection, connection, **database_names):
        self.names = {}
        # db prefix is used to run tests or using the same couchdb instance for multiple api versions
        # like, cs_1234_tenders, prod_tenders, sandbox_tenders, etc
        db_prefix = os.environ.get("DB_NAME_PREFIX", "")
        # init database objects
        for key in self.keys():
            db_name = database_names.get(key)
            # db_name defaults to key
            if not db_name:
                db_name = f"{db_prefix}_{key}" if db_prefix else key
            self.names[key] = db_name
            # ensure db exists
            if db_name not in admin_connection:
                admin_connection.create(db_name)
            # security update (this closes anonymous access to the db)
            # SECURITY is updated from set_api_security during the initial database installation
            if admin_connection is not connection:  # "couchdb.admin_url" in settings
                admin_db = admin_connection[db_name]
                if SECURITY != admin_db.security:
                    LOGGER.info(f"Updating api db {db_name} security", extra={"MESSAGE_ID": "update_api_security"})
                    admin_db.security = SECURITY

            # setting db as attribute to access from code, like `registry.databases.submissions.get(uuid)`
            setattr(self, key, connection[db_name])

        # sync design (creates views)
        sync_design_databases(admin_connection, self.names)

    @classmethod
    def keys(cls):
        return tuple(f.name for f in fields(cls) if f.type is Database)

    def __getitem__(self, item):
        """
        `databases.tenders == databases['tenders']`
        :param item:
        :return:
        """
        return getattr(self, item)


def build_derived_key(password, user_document):
    """
    Builds the hash of a password the same way CouchDB does
    :param password:
    :param user_document:
    :return:
    """
    result = PBKDF2(
        password,
        user_document.get("salt", ""),
        user_document.get("iterations", 10)
    ).hexread(int(len(user_document.get("derived_key", "")) / 2))
    return result


def set_api_security(settings):
    # CouchDB connection
    db_name = os.environ.get("DB_NAME", settings["couchdb.db_name"])
    server = Server(settings.get("couchdb.url"), session=Session(retry_delays=list(range(10))))

    # removing provided credentials from url and create a new connection without any ??
    if "couchdb.admin_url" not in settings and server.resource.credentials:
        try:
            server.version()
        except Unauthorized:
            server = Server(extract_credentials(settings.get("couchdb.url"))[0])

    # admin_url is provided and url contains credentials
    if "couchdb.admin_url" in settings and server.resource.credentials:
        # init admin connection
        aserver = Server(settings.get("couchdb.admin_url"), session=Session(retry_delays=list(range(10))))

        # updating _users security for "_users" database ??
        # in fact this drops security as "names" are empty at the moment
        users_db = aserver["_users"]
        if SECURITY != users_db.security:
            LOGGER.info("Updating users db security", extra={"MESSAGE_ID": "update_users_security"})
            users_db.security = SECURITY

        # non admin user credentials from couchdb.url
        username, password = server.resource.credentials
        # update non-admin user's password ??
        user_doc = users_db.get("org.couchdb.user:{}".format(username), {"_id": "org.couchdb.user:{}".format(username)})
        if not user_doc.get("derived_key", "") \
           or build_derived_key(password, user_doc) != user_doc.get("derived_key", ""):
            user_doc.update({"name": username, "roles": [], "type": "user", "password": password})
            LOGGER.info("Updating api db main user", extra={"MESSAGE_ID": "update_api_main_user"})
            users_db.save(user_doc)

        # adding  non-admin user to SECURITY["members"]["names"] ??
        security_users = [username]

        # updating reader user password and adding it to SECURITY["members"]["names"]
        if "couchdb.reader_username" in settings and "couchdb.reader_password" in settings:
            reader_username = settings.get("couchdb.reader_username")
            reader_password = settings.get("couchdb.reader_password")
            reader = users_db.get(
                "org.couchdb.user:{}".format(reader_username), {"_id": "org.couchdb.user:{}".format(reader_username)}
            )
            if not reader.get("derived_key", "") \
               or build_derived_key(reader_password, reader) != reader.get("derived_key", ""):
                reader.update(
                    {
                        "name": reader_username,
                        "roles": ["reader"],
                        "type": "user",
                        "password": reader_password,
                    }
                )
                LOGGER.info("Updating api db reader user", extra={"MESSAGE_ID": "update_api_reader_user"})
                users_db.save(reader)
            security_users.append(reader_username)

        # ensure database exists
        if db_name not in aserver:
            aserver.create(db_name)

        # updating application database SECURITY
        db = aserver[db_name]
        SECURITY["members"]["names"] = security_users
        if SECURITY != db.security:
            LOGGER.info("Updating api db security", extra={"MESSAGE_ID": "update_api_security"})
            db.security = SECURITY

        # updating validation document
        # VALIDATE_DOC_UPDATE: 1) forbids deleting documents with the tenderId field
        # 2) allows _design document updates for users with _admin role (
        # Is this forbidden without this doc? No -_-, It works for `username` as well
        # 3) allows updates only for `username` (user from couchdb.url), any other user cannot update anything
        # seems application can perfectly work without this
        auth_doc = db.get(VALIDATE_DOC_ID, {"_id": VALIDATE_DOC_ID})
        if auth_doc.get("validate_doc_update") != VALIDATE_DOC_UPDATE % username:
            auth_doc["validate_doc_update"] = VALIDATE_DOC_UPDATE % username
            LOGGER.info("Updating api db validate doc", extra={"MESSAGE_ID": "update_api_validate_doc"})
            db.save(auth_doc)
        # sync couchdb views
        sync_design(db)
        db = server[db_name]
    else:
        # ensure database exists
        # in fact non admin user can't do this
        if db_name not in server:
            server.create(db_name)
        db = server[db_name]
        # sync couchdb views
        sync_design(db)
        aserver = None
    return aserver, server, db


def bootstrap_api_security():
    parser = argparse.ArgumentParser(description="---- Bootstrap API Security ----")
    parser.add_argument("section", type=str, help="Section in configuration file")
    parser.add_argument("config", type=str, help="Path to configuration file")
    params = parser.parse_args()
    if os.path.isfile(params.config):
        conf = ConfigParser()
        conf.read(params.config)
        settings = {k: v for k, v in conf.items(params.section)}
        set_api_security(settings)


#  mongodb
class MongodbResourceConflict(Exception):
    """
    On doc update we pass _id and _rev as filter
    _rev can be changed by concurrent requests
    then update_one(or replace_one) doesn't find any document to update and returns matched_count = 0
    that causes MongodbResourceConflict that is shown to the User as 409 response code
    that means they have to retry his request
    """


def fallback_encoder(value):
    if isinstance(value, Decimal):
        return Decimal128(value)
    return value


type_registry = TypeRegistry(fallback_encoder=fallback_encoder)
codec_options = CodecOptions(type_registry=type_registry)
COLLECTION_CLASSES = {}


class MongodbStore:

    def __init__(self, settings):
        db_name = os.environ.get("DB_NAME", settings["mongodb.db_name"])
        mongodb_uri = os.environ.get("MONGODB_URI", settings["mongodb.uri"])

        # https://docs.mongodb.com/manual/core/causal-consistency-read-write-concerns/#causal-consistency-and-read-and-write-concerns
        raw_read_preference = os.environ.get(
            "READ_PREFERENCE",
            settings.get("mongodb.read_preference", "SECONDARY_PREFERRED")
        )
        raw_w_concert = os.environ.get(
            "WRITE_CONCERN",
            settings.get("mongodb.write_concern", "majority")
        )
        raw_r_concern = os.environ.get(
            "READ_CONCERN",
            settings.get("mongodb.read_concern", "majority")
        )
        self.connection = MongoClient(mongodb_uri)
        self.database = self.connection.get_database(
            db_name,
            read_preference=getattr(ReadPreference, raw_read_preference),
            write_concern=WriteConcern(w=int(raw_w_concert) if raw_w_concert.isnumeric() else raw_w_concert),
            read_concern=ReadConcern(level=raw_r_concern),
            codec_options=codec_options,
        )

        # code related to specific packages, like:
        # store.plans.get(uid) or store.tenders.save(doc) or store.tenders.count(filters)
        for name, cls in COLLECTION_CLASSES.items():
            setattr(self, name, cls(self, settings))

    def get_sequences_collection(self):
        return self.database.sequences

    def get_next_sequence_value(self, uid):
        collection = self.get_sequences_collection()
        result = collection.find_one_and_update(
            {'_id': uid},
            {"$inc": {"value": 1}},
            return_document=ReturnDocument.AFTER,
            upsert=True
        )
        return result["value"]

    def flush_sequences(self):
        collection = self.get_sequences_collection()
        self.flush(collection)

    @staticmethod
    def get_next_rev(current_rev=None):
        """
        This mimics couchdb _rev field
        that prevents concurrent updates
        :param current_rev:
        :return:
        """
        if current_rev:
            version, _ = current_rev.split("-")
            version = int(version)
        else:
            version = 1
        next_rev = f"{version + 1}-{uuid4().hex}"
        return next_rev

    @staticmethod
    def get(collection, uid):
        res = collection.find_one(
            {'_id': uid},
            projection={"is_public": False, "is_test": False, "public_modified": False}
        )
        return res

    def list(self, collection, fields, offset_field="_id", offset_value=None, mode="all", descending=False, limit=0):
        filters = {"is_public": True}
        if mode == "test":
            filters["is_test"] = True
        elif mode != "_all_":
            filters["is_test"] = False
        if offset_value:
            filters[offset_field] = {"$gt": offset_value}
        results = list(collection.find(
            filter=filters,
            projection={f: 1 for f in fields | {offset_field}},
            limit=limit,
            sort=((offset_field, DESCENDING if descending else ASCENDING),)
        ))
        for e in results:
            self.rename_id(e)
        return results

    def save_data(self, collection, data, insert=False):
        uid = data.pop("id" if "id" in data else "_id")
        revision = data.pop("rev" if "rev" in data else "_rev", None)

        data['_id'] = uid
        data["_rev"] = self.get_next_rev(revision)
        data["is_public"] = data.get("status") != "draft"
        data["is_test"] = data.get("mode") == "test"
        data["public_modified"] = datetime.fromisoformat(data["dateModified"]).timestamp()
        if insert:
            data["dateCreated"] = data["dateModified"]
            collection.insert_one(data)
        else:
            result = collection.replace_one(  # replace one also deletes fields ($unset)
                {
                    "_id": uid,
                    "_rev": revision
                },
                data
            )
            if result.matched_count == 0:
                raise MongodbResourceConflict("Conflict while updating document. Please, retry")
        return data

    @staticmethod
    def flush(collection):
        result = collection.delete_many({})
        return result

    @staticmethod
    def rename_id(obj):
        if obj:
            obj["id"] = obj.pop("_id")
        return obj

