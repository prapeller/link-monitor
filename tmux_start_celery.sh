#!/bin/bash

session="celery"

tmux start-server

tmux new-session -d -s $session -n celery

tmux selectp -t 1
tmux send-keys "celery -A celery_tasks worker --loglevel=INFO" C-m

tmux splitw -h
tmux send-keys "docker run --name redis_tmux -p 6379:6379 redis" C-m

#tmux splitw -h
#tmux send-keys "celery -A celery_tasks beat" C-m

tmux splitw -h
tmux send-keys "celery -A celery_tasks flower --loglevel=INFO" C-m

#tmux select-layout even-horizontal

tmux attach-session -t $session