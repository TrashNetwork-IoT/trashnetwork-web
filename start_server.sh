#!/usr/bin/env bash

python ./manage.py runserver 0.0.0.0:23000 > trashnetwork-web-stdout.log 2> trashnetwork-web-stderr.log &
