#!/bin/bash

script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
(
  cd "${script_path}"
  molecule --base-config molecule/molecule_base_lxd_ubuntu.yml test --scenario-name linux_server_setup
  # molecule --base-config molecule/molecule_base_lxd_linux.yml test --scenario-name linux_server_setup
)