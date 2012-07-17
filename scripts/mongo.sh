rm -f /opt/todo-db/mongod.lock
/opt/mongodb-1.8.2/bin/mongod --fork --dbpath=/opt/todo-db --logpath /var/log/mongod.log --logappend
