#!/bin/bash

session="celery"

tmux start-server

tmux new-session -d -s $session

tmux send-keys "cd .." C-m
tmux send-keys "export DEBUG=True && celery -A celery_app worker --loglevel=INFO" C-m

tmux splitw -h

tmux send-keys "cd .." C-m
tmux send-keys "export DEBUG=True && celery -A celery_app flower --loglevel=INFO" C-m

#tmux select-layout even-horizontal

tmux attach-session -t $session
