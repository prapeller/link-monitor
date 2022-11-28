#!/bin/bash

session="dev-local"

tmux start-server

tmux new-session -d -s $session -n dev-local

tmux selectp -t 1
tmux send-keys "ssh dev-local.remote.com -L 127.0.0.1:5555:127.0.0.1:5555" C-m

tmux splitw -h
tmux send-keys "ssh dev-local.remote.com -L 127.0.0.1:5006:127.0.0.1:5006" C-m

tmux attach-session -t $session