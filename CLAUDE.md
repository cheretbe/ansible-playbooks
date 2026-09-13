# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Keep this file current.** When a change alters the repo's structure or its working
principles — the test stack or driver choice, the lint setup, role layout or naming
conventions, the Taskfile interface, the supported distribution matrix, or a documented
workaround that is no longer needed — update the affected section in the same change, and say
so in the commit. Routine work (a new role following the existing conventions, a bug fix, a
version bump) does not need an edit here. Stale guidance is worse than none: if something in
this file contradicts what you find in the repo, trust the repo and fix the file.

## What this repo is

A personal collection of Ansible roles and playbooks for provisioning Linux servers, Windows
workstations and MikroTik routers (Debian/Ubuntu, Proxmox, Zabbix, BackupPC, burp, Docker,
OpenVPN). There is **no inventory in the repo** — playbooks are run against an inventory kept
outside it, so nothing here is runnable end-to-end without one.

## Commands

Everything goes through [go-task](https://taskfile.dev/) (`Taskfile.yml` at the root). The
python venv in `.venv/` is created automatically on first use from `requirements.txt` +
`dev_requirements.txt`; `task venv:rebuild` recreates it. Needs
`python3-venv build-essential python3-dev` on the host (checked as a precondition).

```shell
cd roles/<role>
task test                     # ansible-lint, then 'molecule test --all'
task lint                     # ansible-lint on the current directory
task converge -- -s upgrade   # single scenario; args after -- go to molecule
task verify
task login -- -h debian-13    # shell on a converged instance
task destroy
task molecule -- list         # arbitrary molecule command
```

Run `task lint` from the repo root to lint everything. Most task commands use
`{{.USER_WORKING_DIR}}`, so the role directory you are in selects what runs — except `lint`,
which always executes with cwd = repo root (see Linting below).

Molecule runs take minutes (and VM boots for `linux-provision`). When polling one in the
background, sleep ~100s between checks, not 5–10 minutes.

## Architecture

**Playbooks are thin.** The root `*.yml` playbooks mostly just import or include one role;
logic belongs in `roles/`. `run_role.yml` runs an arbitrary role via `-e role_name=...`.

**Role layout conventions** (clearest in `roles/linux_seafile_cli`, the newest role):

- `defaults/main.yml` — public inputs, all prefixed `<role_name>_`, commented with *why* a
  value is what it is. Required inputs default to `""` and are checked by an
  `ansible.builtin.assert` at the top of `tasks/main.yml`.
- `vars/main.yml` — values *derived* from the inputs, prefixed `_<role_name>_`, not meant to
  be set by the caller.
- `meta/argument_specs.yml` — present on newer roles (`linux_seafile_cli`, `zabbix-agent2`,
  `zabbix-monitored-host`); add one when touching or adding a role.
- Roles added from 2025 on use **underscores** (`linux_seafile_cli`); older ones are
  hyphenated (`linux-provision`). Hence `role-name` is the one entry in the lint skip list.

**Facts are read via `ansible_facts[...]` only** — never the injected top-level vars
(`ansible_distribution` etc.). The molecule base config sets
`ANSIBLE_INJECT_FACT_VARS: "false"` so the removal in ansible-core 2.24 surfaces now, as an
undefined-variable error rather than a deprecation warning. ansible-lint has no rule for
this; the runtime setting is the only enforcement.

**Custom code:** `library/` (modules) and `action_plugins/` (`display_warning`) are picked up
implicitly by their directory names. `tools/` holds standalone operator scripts, unrelated to
playbook runs.

## Testing (molecule)

- **Docker is the default driver.** `.config/molecule/config.yml` is the shared base config,
  auto-discovered via the VCS root from any role directory; it defines the whole platform
  matrix (debian 11/12/13, ubuntu 22.04/24.04 on `geerlingguy/docker-*-ansible`), the
  provisioner env and the test sequence. A scenario `molecule.yml` overrides per key — dicts
  merge recursively, **lists (e.g. `platforms`) are replaced wholesale**. Most scenarios
  therefore contain nothing but `driver: name: docker`.
- **Vagrant only where containers can't test the behaviour** (systemd, hostname, DNS). The
  only vagrant consumer is `linux-provision`, which overrides driver *and* platforms inline.
- **Do not propose lxd, pyinvoke or make.** The lxd driver was dropped. `tests/molecule/*.yml`
  (the old base-config matrix, including `molecule_base_lxd_*.yml`), `tests/test_utils.py` and
  the per-role `tasks.py` pyinvoke wrappers are dead leftovers awaiting deletion — don't
  extend them or copy their patterns.
- If the geerlingguy images ever go unmaintained, the agreed fallback is building local
  systemd images (`pre_build_image: false` + `Dockerfile.j2`), not switching to vagrant. The
  platforms live in one place to make that a single edit.
- `temp/old/` archives retired roles (`awx-server`, `backuppc-server`, `nagios-client`,
  `terraform-apply`); it is excluded from linting.

### Debian 11 in the test matrix

Debian 11 LTS ended 2026-08-31 and bullseye-security broke shortly after, so
`roles/linux-provision/molecule/default/prepare.yml` strips the `security.debian.org` line
from `sources.list` and disables `Acquire::Check-Valid-Until` on Debian 11 instances. Keep
that in mind before debugging apt failures on bullseye as if they were new — and re-check the
current upstream state before assuming the workaround is still required, as it has been
moving.

## Linting

One root `.ansible-lint` (`profile: production`, `exclude_paths: [temp/]`) and one root
`.yamllint`. **Do not reintroduce per-role lint config** — 18 such files were deleted in
favour of this pair; fix the role instead of adding skips.

Two non-obvious mechanics force `task lint` to run from the repo root with the target passed
as an argument:

1. `.yamllint` is resolved as a bare relative name against the cwd with **no walk up the
   tree**, and ansible-lint never chdirs — a root `.yamllint` is invisible if ansible-lint
   runs inside the role directory. (`.ansible-lint` does walk up, stopping at `.git`.)
2. Role-scoped rules only apply when a `roles/<name>` path is passed; `ansible-lint .` from
   inside a role silently skips them.

ansible-lint hard-validates any custom `.yamllint` against six settings
(`comments.min-spaces-from-content`, `comments-indentation`, `braces.min/max-spaces-inside`,
both `octal-values.forbid-*`) and rejects the file outright if they differ — the marked block
in `.yamllint` must not be changed.

The `production` profile is strict by design and roles are cleaned up **one at a time** as
they are picked up, so a role that hasn't been touched yet is expected to fail lint. That is
not a regression you introduced; fix the role or leave it, but don't widen `skip_list`.

## Conventions

- Commit subjects: `roles/<role-name>: lowercase description`, or a plain sentence for
  repo-wide changes. Work happens on `develop`; `master` is the main branch.
- Comments in tasks and defaults explain *why* (upstream quirks, ordering constraints,
  idempotency guards), not what the module does. Match that density when editing.
