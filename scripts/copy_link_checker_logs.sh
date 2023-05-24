#!/bin/bash

session="link_checker"

tmux start-server

tmux new-session -d -s $session

tmux send-keys "  # window 1, pane 0 (dev-local.kaisaco.com://report.backend)" C-m
tmux send-keys "ssh dev-local.kaisaco.com" C-m
tmux send-keys "docker cp report.backend:/app/services/link_checker/link_checker.log /home/pavelmirosh/" C-m
sleep 6

tmux splitw -h
tmux send-keys "  # window 1, pane 1 (localhost)" C-m
tmux send-keys "scp dev-local.kaisaco.com:/home/pavelmirosh/link_checker.log ../services/link_checker/" C-m
sleep 6

tmux selectp -t 0
tmux send-keys "rm /home/pavelmirosh/link_checker.log" C-m

tmux attach-session -t $session
