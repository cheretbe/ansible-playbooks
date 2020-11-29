#!/bin/bash

set -euo pipefail

if [ -z ${1+x} ]; then
  echo >&2 "ERROR: Mandatory parameter is missing (Ansible user name)"
  exit 1
fi

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Reading public key from '${script_dir}/ansible_user_key.pub'"
public_key=$(cat "${script_dir}/ansible_user_key.pub")

if id -u "${1}" >/dev/null 2>&1; then
  echo "User '${1}' already exists"
else
  adduser --disabled-password --gecos "" "${1}"
fi

if /bin/grep -q "${public_key}" /home/${1}/.ssh/authorized_keys >/dev/null 2>&1; then
  echo "'/home/${1}/.ssh/authorized_keys' already contains the SSH key"
else
  echo "Adding key ${public_key}"
  echo "to '/home/${1}/.ssh/authorized_keys' file"
  mkdir -p /home/${1}/.ssh
  echo "${public_key}">>/home/${1}/.ssh/authorized_keys
  echo "Setting permissions"
  chown ${1}:${1} /home/${1}/.ssh
  chmod 700 /home/${1}/.ssh
  chown ${1}:${1} /home/${1}/.ssh/authorized_keys
  chmod 600 /home/${1}/.ssh/authorized_keys
fi

tmpfile=$(mktemp)
echo "${1} ALL=(ALL) NOPASSWD:ALL" >"${tmpfile}"
visudo -cf "${tmpfile}"
echo "Writing '/etc/sudoers.d/ansible_user' file"
mv "${tmpfile}" /etc/sudoers.d/ansible_user
