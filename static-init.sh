#!/bin/bash
# sudo -u pretixuser pretix collectstatic --noinput && sudo -u pretixuser pretix compress && cd /pretix-paybox && make && supervisorctl -s unix:///tmp/supervisor.sock restart pretixweb
NS=pretix
POD=$(kubectl -n $NS get pods | grep "pretix-" | cut -d' ' -f1)
    kubectl -n $NS exec $POD -- bash -c "sudo -u pretixuser pretix collectstatic --noinput && sudo -u pretixuser pretix compress"
    kubectl -n $NS exec $POD -- bash -c "cd /pretix-paybox && make"
    kubectl -n $NS exec $POD -- bash -c "supervisorctl -s unix:///tmp/supervisor.sock restart pretixweb"