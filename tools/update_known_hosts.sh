#!/bin/bash

# install -m 600 /dev/null ~/.ssh/known_hosts
(umask 066; touch ~/.ssh/known_hosts)
#ssh-keygen -q -F ubuntu-bionic || ssh-keyscan -t rsa ubuntu-bionic >> /root/.ssh/known_hosts
ansible all --list-hosts | sed 1d | xargs -L 1 -I {} bash -c "ssh-keygen -q -F {} || ssh-keyscan -t rsa {} >>~/.ssh/known_hosts"