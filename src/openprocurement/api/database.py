# -*- coding: utf-8 -*-
import argparse
import os
from pbkdf2 import PBKDF2
from configparser import ConfigParser
from couchdb import Server as CouchdbServer, Session, Database
from couchdb.http import Unauthorized, extract_credentials
from openprocurement.api.design import sync_design, sync_design_databases
from logging import getLogger
from dataclasses import dataclass, fields

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
