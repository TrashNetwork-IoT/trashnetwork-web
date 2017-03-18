# trashnetwork-web
The web server of TrashNetwork project.

## Prerequisite

+ Python 3
+ MySQL
+ Redis
+ Python modules(It‘s recommended to install via `PyPI`):
  + pillow 
  + django
  + django-redis-cache
  + djangorestframework
  + hiredis
  + mysqlclient
  + paho-mqtt
  + geopy

## Build and Start

1. Init database as MySQL root user:

```shell
mysql -uroot -p -e "source init_db.sql"
```

2. Migrate database models:

```shell
python ./manage.py makemigrations trashnetwork
python ./manage.py migrate
```

3. Compile message resource:

```shell
python ./manage.py compilemessages
```

4. Start server:

```shell
# Start server at port 23000
python ./manage.py runserver 0.0.0.0:23000
```
## Start Server at Backend

You can execute `start_server.sh`  to start server at port 23000 at backend directly.

## Sync Code to Remote Host

You can use `sync.sh` to sync your code to remote host. This script will sync your code via `rsync`.

Basic usage of `sync.sh`:

```shell
sync.sh ${REMOTE_HOST}
```

`$REMOTE_HOST` refer to address of remote host that you want to sync code to.

By default, remote user is `happyyoung`, and syncing path on remote host is `/home/happyyoung/trashnetwork-web`.