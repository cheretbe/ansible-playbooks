#!/bin/bash

script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
(
  cd "${script_path}/../.."

  if [ -z "$1" ]; then
    hosts_param=""
  else
    hosts_param="--hosts=${1}"
  fi

  py.test -v --connection=ansible ${hosts_param}\
    linux-utils/tests \
    linux-dns/tests \
    linux-locale/tests \
    linux-mta/tests \
    linux-timezone/tests \
    linux-unattended-upgrades/tests \
    smartmontools/tests
)
