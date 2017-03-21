#!/usr/bin/env bash

tmux new-session -d -s TrashNetwork \
 "unset SSH_CLIENT;
  unset SSH_CONNECTION;
  unbuffer -p python3 ./manage.py runserver 0.0.0.0:23000 2>&1 | tee -ai trashnetwork-web.log"
