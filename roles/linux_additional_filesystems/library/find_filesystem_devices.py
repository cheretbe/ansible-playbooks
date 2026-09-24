#!/usr/bin/python

# The shebang must be the conventional /usr/bin/python: Ansible only remaps a
# module's interpreter to the one it discovers (ansible_python_interpreter=auto)
# when the shebang's interpreter is 'python'. A '/usr/bin/env python3' shebang is
# left literal and the target then runs '/usr/bin/env python3', which fails.

# Resolve each requested filesystem to a concrete block device by matching the
# expected disk size against gathered facts, instead of trusting a caller-supplied
# /dev/sdX name (which the kernel can reassign across reboots). Any assignment that
# already exists - active mount or fstab entry - is honoured and only validated, so
# re-runs never reshuffle disks or format the wrong one.
#
# The block-device inventory (ansible_facts.devices) and the current mount table
# (ansible_facts.mounts) are injected by the paired action plugin; this module only
# runs 'lsblk'/'findmnt' on the target for the parts facts cannot answer.

import os
import string

from ansible.module_utils.basic import AnsibleModule


def get_root_device_name(module):
    result = None
    # run_command returns: rc, stdout, stderr
    # -n      don't print headings
    # PKNAME  internal parent kernel device name (retuns correct result both for
    #         physical disks and LVM)
    for line in module.run_command("lsblk -n -oMOUNTPOINT,PKNAME", check_rc=True)[1].splitlines():
        output = line.split()
        if len(output) > 1:
            if output[0].strip() == "/":
                # May contain sda, sda1, vda, vda1 etc. We need the device name without partition number
                result = output[1].strip().rstrip(string.digits)
    return result


def _source_path(source):
    source_types = {
        "UUID": "by-uuid",
        "LABEL": "by-label",
        "PARTUUID": "by-partuuid",
        "PARTLABEL": "by-partlabel",
    }
    if source.startswith("/dev/"):
        return os.path.realpath(source)
    source_type, separator, value = source.partition("=")
    if not separator or source_type not in source_types:
        return None
    value = value.strip("\"'")
    return os.path.realpath(f"/dev/disk/{source_types[source_type]}/{value}")


def _get_source_device(module, source):
    source_path = _source_path(source)
    if not source_path:
        return None, None
    output = module.run_command(
        ["lsblk", "-n", "-o", "PKNAME", source_path],
        check_rc=True,
    )[1].strip()
    if output:
        return source_path, output.splitlines()[0].strip()
    return source_path, os.path.basename(source_path)


def _get_fstab_sources(module, fstab_path, mount_path):
    if not os.path.exists(fstab_path):
        return set()

    command = [
        module.get_bin_path("findmnt", required=True),
        "--fstab",
        "--evaluate",
        "--noheadings",
        "--raw",
        "--output",
        "SOURCE",
        "--target",
        mount_path,
    ]
    if fstab_path != "/etc/fstab":
        command.extend(["--tab-file", fstab_path])

    rc, stdout, stderr = module.run_command(command)
    if rc == 1 and not stderr.strip():
        return set()
    if rc != 0:
        module.fail_json(
            msg=f"Can't read fstab entry for {mount_path}: {stderr.strip() or stdout.strip()}"
        )
    return {source for source in stdout.splitlines() if source}


def _get_existing_device(module, item, mounts, fstab_path):
    mount_path = item["mount_path"]
    active_sources = {
        mount["device"]
        for mount in mounts
        if mount.get("mount") == mount_path and mount.get("device")
    }
    configured_sources = _get_fstab_sources(module, fstab_path, mount_path)

    if len(active_sources) > 1:
        module.fail_json(msg=f"Multiple active devices found for {mount_path}")
    if len(configured_sources) > 1:
        module.fail_json(msg=f"Multiple fstab devices found for {mount_path}")

    active_source, active_device = (
        _get_source_device(module, next(iter(active_sources)))
        if active_sources
        else (None, None)
    )
    configured_source, configured_device = (
        _get_source_device(module, next(iter(configured_sources)))
        if configured_sources
        else (None, None)
    )

    if active_sources and not active_device:
        module.fail_json(msg=f"Can't resolve active device for {mount_path}")
    if configured_sources and not configured_device:
        module.fail_json(msg=f"Can't resolve fstab device for {mount_path}")
    if active_source and configured_source and active_source != configured_source:
        module.fail_json(
            msg=(
                f"Active source {active_source} and fstab source "
                f"{configured_source} differ for {mount_path}"
            )
        )
    return active_device or configured_device


def _get_size_to_find(item):
    if isinstance(item["disk_size"], (int, float)):
        return "{:.2f} GB".format(item["disk_size"])
    return item["disk_size"]


def _assign_filesystem_devices(module, filesystem_list, devices, mounts, fstab_path):
    root_device = get_root_device_name(module)
    used_devices = set()
    assignments = []

    for item in filesystem_list:
        size_to_find = _get_size_to_find(item)
        found_device = _get_existing_device(module, item, mounts, fstab_path)

        if found_device:
            if found_device == root_device:
                module.fail_json(msg=f"Root device can't be used for {item['mount_path']}")
            if found_device not in devices:
                module.fail_json(
                    msg=f"Device /dev/{found_device} for {item['mount_path']} is absent from facts"
                )
            if devices[found_device]["size"] != size_to_find:
                module.fail_json(
                    msg=(
                        f"Device /dev/{found_device} for {item['mount_path']} has size "
                        f"{devices[found_device]['size']}, expected {size_to_find}"
                    )
                )
            if found_device in used_devices:
                module.fail_json(
                    msg=f"Device /dev/{found_device} is assigned to multiple mount points"
                )
            used_devices.add(found_device)

        assignments.append((item, size_to_find, found_device))

    for item, size_to_find, found_device in assignments:
        if not found_device:
            found_device = next(
                (
                    device
                    for device in sorted(devices)
                    if device != root_device
                    and device not in used_devices
                    and devices[device]["size"] == size_to_find
                ),
                None,
            )

        if not found_device:
            module.fail_json(
                msg=f"Can't find disk of size {size_to_find} for {item['mount_path']}"
            )

        used_devices.add(found_device)
        item["device"] = f"/dev/{found_device}"

    return filesystem_list


def main():
    module_args = dict(
        filesystem_list=dict(type="list", elements="dict", required=True),
        devices=dict(type="dict", required=True),
        mounts=dict(type="list", elements="dict", default=[]),
        fstab=dict(type="path", default="/etc/fstab"),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    result_list = _assign_filesystem_devices(
        module,
        module.params["filesystem_list"],
        module.params["devices"],
        module.params["mounts"],
        module.params["fstab"],
    )

    result = dict(
        changed=False,
        filesystems=result_list,
    )
    module.exit_json(**result)


if __name__ == "__main__":
    main()
