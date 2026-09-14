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
task test:one                 # ansible-lint, then the molecule sequence on ONE platform
task test                     # ansible-lint, then 'molecule test --all' (whole matrix)
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

### Test one platform first

**Always gate on `task test:one` before spending a `task test`.** It runs the full
destroy → create → prepare → converge → idempotence → verify → destroy sequence against a
single instance, so a mistake in the role surfaces after one VM boot instead of five.

```shell
cd roles/linux_provision
task test:one -- debian-13.local.test   # vagrant roles: the platform name is an FQDN
cd roles/docker-ce
task test:one                           # docker roles: defaults to 'debian-13'
task test                               # only once test:one is green
```

The mechanism is `molecule test --platform-name <name>`, which filters molecule's own
platform list, so `create`/`prepare`/`destroy` touch that one instance too. Two gotchas:

- `--platform-name` exists **only on `molecule test`** — not on `create`, `converge`,
  `verify`, `login` or `destroy`. There is no way to converge a single platform; the
  scenario's `platforms` list is all-or-nothing for those.
- The name must match `platforms[].name` exactly. Docker scenarios inherit `debian-13` from
  the base config; `linux_provision` overrides platforms with FQDNs
  (`debian-13.local.test`), because the role asserts `inventory_hostname == fqdn`.

**Why it matters:** a guest that cannot boot looks exactly like a role failure and costs 15
minutes to find out it isn't — vagrant just loops on "Connection reset" until
`vm.boot_timeout` (900s) expires. Deleting cached VirtualBox base boxes makes it worse still,
since the next run re-imports all five while booting them.

### Always set `memory`/`cpus` on vagrant platforms

The molecule vagrant driver defaults every instance to **512MB and 2 vCPUs**
(`instance.get("memory", 512)` in `molecule_plugins/vagrant/modules/vagrant.py`), *overriding
whatever the box ships with*. 512MB is enough for a minimal Debian but not for Ubuntu, which
then wedges mid-boot instead of failing cleanly: `systemd-tmpfiles-setup.service` running
with **"no limit"** while `sd-mkdcreds` and `systemd-networkd` sit blocked in D state, plus
`rcu_preempt` stalls. Symptom is an intermittent hang on `ubuntu-24.04` only.

`roles/linux_provision/molecule/default/molecule.yml` therefore sets `memory` and `cpus` per
platform (1024 for Debian, 2048 for Ubuntu, `cpus: 1` everywhere — five instances at the
default 2 vCPUs oversubscribe a 6-core host, and these VMs are IO-bound on apt anyway).
Diagnose a suspected hang with `VBoxManage controlvm <uuid> screenshotpng /tmp/vm.png` and
read the console; `VBoxManage showvminfo <uuid> --machinereadable | grep -E '^memory=|^cpus='`
shows what the instance actually got.

Molecule runs take minutes (and VM boots for `linux_provision`). When polling one in the
background, sleep ~50s between checks, not 5–10 minutes.

`task lint` is invoked as a sub-task by both `test` and `test:one` with an explicit `TARGET`
var. Without it the sub-task inherits the caller's `CLI_ARGS` and ansible-lint tries to lint
the platform name as a path.

## Architecture

**Playbooks are thin.** The root `*.yml` playbooks mostly just import or include one role;
logic belongs in `roles/`. `run_role.yml` runs an arbitrary role via `-e role_name=...`.

**Role layout conventions** (`roles/linux_seafile_cli` for a single-purpose role,
`roles/linux_provision` for a multi-step one):

- `defaults/main.yml` — public inputs, all prefixed `<role_name>_`, commented with *why* a
  value is what it is. Required inputs default to `""` and are checked by an
  `ansible.builtin.assert` at the top of `tasks/main.yml`.
- `vars/main.yml` — values *derived* from the inputs, prefixed `_<role_name>_`, not meant to
  be set by the caller.
- `meta/argument_specs.yml` — present on newer roles (`linux_provision`,
  `linux_seafile_cli`, `zabbix-agent2`, `zabbix-monitored-host`); add one when touching or
  adding a role.
- Roles added from 2025 on use **underscores** (`linux_provision`, `linux_seafile_cli`);
  older ones are hyphenated (`docker-ce`). `.ansible-lint` has **no** `skip_list`, so a
  hyphenated role fails `role-name` — that is expected until it is picked up and renamed.

**Variable prefixes** (enforced by convention, not by a lint rule):

| Prefix | Meaning | Where |
|--------|---------|-------|
| `<role_name>_*` | public input, caller-settable | `defaults/main.yml` |
| `_<role_name>_*` | derived value, `set_fact` result, `loop_var` name | `vars/main.yml`, task files |
| `__<role_name>_*` | `register:` target | task files |

`roles/linux_seafile_cli` predates the `__` tier and uses single `_` for its `register:`
targets; it stays as it is. `roles/linux_provision` is the reference for new work.

**A role never calls another role.** Steps that depend on each other live in the same role as
task files imported in dependency order by `tasks/main.yml` — see `roles/linux_provision`,
where `mta.yml` is placed before `smartmontools.yml` because the smartmontools package pulls
in postfix. Reaching sideways with `include_role: name="{{ role_path }}/../other-role"` is
what the absorbed roles used to do; the three remaining call sites (`ovpn-server`,
`ovpn-client`, `router`, all for the old `linux-dns`) are commented out and should become a
play of their own, not be revived.

### Running one step of a multi-step role

**`tasks_from`, not tags.** A playbook cannot select tags — `tags:` on `import_role` is
*appended* to every task in the role, it does not filter; only `--tags` on the command line
selects. So a "run just the MOTD part" playbook written with tags silently provisions the
whole host when run without the flag. `roles/linux_provision` therefore carries no tags and
no task-selector variables at all: `tasks/main.yml` is a flat, unconditional list of
`import_tasks`, and each per-task playbook names its file.

```yaml
# linux_motd.yml
tasks:
  # importing a single task file bypasses tasks/main.yml, so the FQDN and
  # distribution checks have to be asked for explicitly
  - name: Check host
    ansible.builtin.import_role: {name: linux_provision, tasks_from: check_host}
  - name: Configure MOTD
    ansible.builtin.import_role: {name: linux_provision, tasks_from: motd}
```

Consequences to keep in mind when adding a task file:

- **Write `tasks_from: motd`, never `motd.yml`.** Ansible uses that string verbatim as the
  `meta/argument_specs.yml` entry-point name (`_prepend_validation_task` does
  `self._from_files.get('tasks', 'main')`; nothing strips the extension). With no matching
  entry point, argument validation is **silently skipped** — no warning. `linux_provision`
  declares only `main`, so the per-task playbooks are deliberately unvalidated; adding entry
  points named after the task files is purely additive if that ever matters.
- **A guard belongs in the task file, not on the import in `main.yml`**, or `tasks_from`
  bypasses it — e.g. the "skip on a VM" condition wraps the body of `smartmontools.yml`.
- Importing the same role twice with different `tasks_from` is safe: `from_files` is part of
  the role's hash, so the two are not de-duplicated.
- Everything else still loads under `tasks_from` — `defaults/`, `vars/` and
  `handlers/main.yml` — so `notify:` inside a single task file keeps working.
- `import_tasks` (static) is preferred over `include_tasks` when there is no condition on the
  include: `--list-tasks` then shows the role's real task list instead of the include lines.

**Facts are read via `ansible_facts[...]` only** — never the injected top-level vars
(`ansible_distribution` etc.). The molecule base config sets
`ANSIBLE_INJECT_FACT_VARS: "false"` so the removal in ansible-core 2.24 surfaces now, as an
undefined-variable error rather than a deprecation warning. ansible-lint has no rule for
this; the runtime setting is the only enforcement.

**Debian/Ubuntu only.** `linux_provision` hard-fails on anything else and the molecule matrix
matches, so it carries no RedHat/CentOS branches — they were unreachable and have been
deleted. Don't re-add `yum`/`dnf` paths, `os_family == "RedHat"` guards or
`when: os_family == "Debian"` no-ops to it.

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
  only vagrant consumer is `linux_provision`, which overrides driver *and* platforms inline.
- **Do not propose lxd, pyinvoke, testinfra or make.** The lxd driver was dropped, and
  verification is `verifier: ansible` (a scenario `verify.yml`), not testinfra.
  `tests/molecule/*.yml` (the old base-config matrix, including `molecule_base_lxd_*.yml`) and
  `tests/test_utils.py` are dead leftovers awaiting deletion — don't extend them or copy their
  patterns. `tests/helper_tasks/{add_test_user,set_local_package_cache}.yml` *are* live and
  still included by several scenarios' `prepare.yml`.
- `linux_provision` has a single vagrant scenario covering all ten of its task files. The
  per-task playbooks are *not* exercised by it — when changing `tasks/main.yml` or a task
  file, check one by hand with
  `ansible-playbook linux_motd.yml --list-tasks` (it must show `check_host` plus that file
  only). A docker
  scenario for the apt/template-only task files would be a reasonable addition.
- **Most roles still have no molecule coverage** — only `linux_provision`,
  `linux_seafile_cli`, `docker-ce`, `backuppc-client`, `backuppc-client-rsync`,
  `zabbix-agent2`, `zabbix-monitored-host` and `zabbix-server` have a `molecule/` directory.
  Where a role once had one, its old scenario (a `lint:` key, testinfra
  verifier + `tests/*.py`, no `driver: docker`, some importing since-removed helper stubs)
  was deleted rather than migrated. Write a new one against the shared docker config when a
  role is next picked up; don't assume the absence means the role is untestable.
- If the geerlingguy images ever go unmaintained, the agreed fallback is building local
  systemd images (`pre_build_image: false` + `Dockerfile.j2`), not switching to vagrant. The
  platforms live in one place to make that a single edit.
- `temp/old/` archives retired roles (`awx-server`, `backuppc-server`, `nagios-client`,
  `terraform-apply`); it is excluded from linting.

### Debian 11 in the test matrix

Debian 11 LTS ended 2026-08-31 and bullseye-security broke shortly after, so
`roles/linux_provision/molecule/default/prepare.yml` strips the `security.debian.org` line
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

**ansible-lint does not follow `include_role`** (it does follow `include_tasks` within a
role). That used to mean `task lint` inside `roles/linux-provision` reached none of the
eleven roles it pulled in at runtime; absorbing them into `roles/linux_provision` as task
files fixed it, and `task lint -- roles/linux_provision` now covers the whole chain. Keep it
that way — a role that includes another role is a role that cannot be linted.

Playbooks are not linted by any role path, so pass them explicitly when you touch one:

```shell
task lint -- linux_provision.yml linux_dns.yml linux_motd.yml linux_users.yml
```

## Conventions

- Commit subjects: `roles/<role-name>: lowercase description`, or a plain sentence for
  repo-wide changes. Work happens on `develop`; `master` is the main branch.
- Comments in tasks and defaults explain *why* (upstream quirks, ordering constraints,
  idempotency guards), not what the module does. Match that density when editing.
