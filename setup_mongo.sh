#!/bin/bash 

# TODO: This script assumes the following
# you named the container where your mongod runs 'mongo'
# you changed MONGO_INITDB_DATABASE to 'test'
# you set MONGO_INITDB_ROOT_USERNAME to 'root'
# you set MONGO_INITDB_ROOT_PASSWORD to 'example'
# you set the replica set name to 'rs0' (--replSet)
until mongosh --host mongo:27017 --eval 'quit(db.runCommand({ ping: 1 }).ok ? 0 : 2)' &>/dev/null; do
  printf '.'
  sleep 1
done

cd /
echo '
try {
    var config = {
        "_id": "rs0", // TODO update this with your replica set name
        "version": 1,
        "members": [
        {
            "_id": 0,
            "host": "mongo:27017", // TODO rename this host
            "priority": 2
        },
        ]
    };
    rs.initiate(config, { force: true });
    rs.status();
    sleep(5000);
    // creates another user
    admin = db.getSiblingDB("admin");
    admin.createUser(
          {
        user: "otheradmin",
        pwd:  "othersecret", 
        roles: [ { role: "readWrite", db: "myowndb" },
             { role: "readWrite", db: "admin" } ,
        
        ]
          }
    );
} catch(e) {
    rs.status().ok
}
' > /config-replica.js



sleep 10
# TODO update user, password, authenticationDatabase and host accordingly
mongosh -u root -p "example" --authenticationDatabase admin --host mongo:27017 /config-replica.js

# if the output of the container mongo_setup exited with code 0, everything is probably okay
