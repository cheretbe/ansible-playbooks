import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

sys.modules["ansible"] = MagicMock()
sys.modules["ansible.module_utils"] = MagicMock()
sys.modules["ansible.module_utils.basic"] = MagicMock()
sys.modules["ansible.plugins"] = MagicMock()
sys.modules["ansible.plugins.action"] = MagicMock()


class MockActionBase:
    pass


sys.modules["ansible.plugins.action"].ActionBase = MockActionBase

from action_plugins.find_filesystem_devices import ActionModule
from library.find_filesystem_devices import (
    _assign_filesystem_devices,
    _get_fstab_sources,
)


class ModuleFailure(Exception):
    pass


class TestGetFstabSources(unittest.TestCase):
    def test_get_fstab_sources(self):
        cases = [
            {
                "name": "default fstab source",
                "fstab": "/etc/fstab",
                "mount": "/var/lib/docker",
                "result": (0, "/dev/sdb1\n", ""),
                "expected": {"/dev/sdb1"},
                "command_suffix": ["--target", "/var/lib/docker"],
            },
            {
                "name": "missing mount point",
                "fstab": "/etc/fstab",
                "mount": "/missing",
                "result": (1, "", ""),
                "expected": set(),
                "command_suffix": ["--target", "/missing"],
            },
            {
                "name": "custom fstab",
                "fstab": "/tmp/fstab",
                "mount": "/srv",
                "result": (0, "/dev/sdc1\n", ""),
                "expected": {"/dev/sdc1"},
                "command_suffix": ["--tab-file", "/tmp/fstab"],
            },
            {
                "name": "findmnt failure",
                "fstab": "/etc/fstab",
                "mount": "/srv",
                "result": (2, "", "invalid fstab"),
                "error": "Can't read fstab entry for /srv: invalid fstab",
            },
        ]

        for case in cases:
            with self.subTest(case["name"]):
                module = Mock()
                module.get_bin_path.return_value = "/usr/bin/findmnt"
                module.run_command.return_value = case["result"]

                def fail_json(**kwargs):
                    raise ModuleFailure(kwargs["msg"])

                module.fail_json.side_effect = fail_json

                with patch(
                    "library.find_filesystem_devices.os.path.exists",
                    return_value=True,
                ):
                    if "error" in case:
                        with self.assertRaisesRegex(ModuleFailure, case["error"]):
                            _get_fstab_sources(module, case["fstab"], case["mount"])
                    else:
                        self.assertEqual(
                            _get_fstab_sources(module, case["fstab"], case["mount"]),
                            case["expected"],
                        )
                        command = module.run_command.call_args.args[0]
                        self.assertEqual(
                            command[-len(case["command_suffix"]) :],
                            case["command_suffix"],
                        )


class TestAssignFilesystemDevices(unittest.TestCase):
    def test_assign_filesystem_devices(self):
        devices = {
            "sda": {"size": "60.00 GB"},
            "sdb": {"size": "60.00 GB"},
            "sdc": {"size": "60.00 GB"},
        }
        filesystems = [
            {"disk_size": 60, "mount_path": "/var/lib/docker"},
            {"disk_size": 60, "mount_path": "/home/gitlab-runner/disk"},
        ]
        cases = [
            {
                "name": "new server uses deterministic device order",
                "mounts": [],
                "fstab": {},
                "parents": {},
                "expected": ["/dev/sdb", "/dev/sdc"],
            },
            {
                "name": "existing assignment ignores device fact order",
                "mounts": [
                    {"mount": "/var/lib/docker", "device": "/dev/sdc1"},
                    {"mount": "/home/gitlab-runner/disk", "device": "/dev/sdb1"},
                ],
                "fstab": {
                    "/var/lib/docker": {"/dev/sdc1"},
                    "/home/gitlab-runner/disk": {"/dev/sdb1"},
                },
                "parents": {
                    "/dev/sdc1": "sdc",
                    "/dev/sdb1": "sdb",
                },
                "expected": ["/dev/sdc", "/dev/sdb"],
            },
            {
                "name": "fstab assignment is reused when not mounted",
                "mounts": [],
                "fstab": {
                    "/var/lib/docker": {"/dev/sdc1"},
                    "/home/gitlab-runner/disk": {"/dev/sdb1"},
                },
                "parents": {
                    "/dev/sdc1": "sdc",
                    "/dev/sdb1": "sdb",
                },
                "expected": ["/dev/sdc", "/dev/sdb"],
            },
            {
                "name": "active and fstab conflict fails",
                "mounts": [{"mount": "/var/lib/docker", "device": "/dev/sdb1"}],
                "fstab": {"/var/lib/docker": {"/dev/sdc1"}},
                "parents": {
                    "/dev/sdb1": "sdb",
                    "/dev/sdc1": "sdc",
                },
                "error": "Active source /dev/sdb1 and fstab source /dev/sdc1 differ",
            },
        ]

        for case in cases:
            with self.subTest(case["name"]):
                module = Mock()

                def fail_json(**kwargs):
                    raise ModuleFailure(kwargs["msg"])

                def run_command(command, check_rc=False):
                    if isinstance(command, str):
                        return 0, "/ sda\n", ""
                    return 0, f"{case['parents'].get(command[-1], '')}\n", ""

                module.fail_json.side_effect = fail_json
                module.run_command.side_effect = run_command
                input_filesystems = [item.copy() for item in filesystems]
                input_devices = dict(reversed(list(devices.items())))

                with (
                    patch(
                        "library.find_filesystem_devices._get_fstab_sources",
                        side_effect=lambda module, fstab_path, mount_path: case[
                            "fstab"
                        ].get(mount_path, set()),
                    ),
                    patch(
                        "library.find_filesystem_devices.os.path.realpath",
                        side_effect=lambda path: path,
                    ),
                ):
                    if "error" in case:
                        with self.assertRaisesRegex(ModuleFailure, case["error"]):
                            _assign_filesystem_devices(
                                module,
                                input_filesystems,
                                input_devices,
                                case["mounts"],
                                "/etc/fstab",
                            )
                    else:
                        result = _assign_filesystem_devices(
                            module,
                            input_filesystems,
                            input_devices,
                            case["mounts"],
                            "/etc/fstab",
                        )
                        self.assertEqual(
                            [item["device"] for item in result],
                            case["expected"],
                        )


class TestActionModule(unittest.TestCase):
    def _run(self, task_vars):
        action_module = ActionModule()
        action_module._task = Mock()
        action_module._task.args = {"filesystem_list": []}
        action_module._execute_module = Mock(
            return_value={"changed": False, "filesystems": []}
        )
        result = action_module.run(task_vars=task_vars)
        return action_module, result

    def test_run_reads_ansible_facts(self):
        # This repo runs with ANSIBLE_INJECT_FACT_VARS=false, so facts arrive only
        # under ansible_facts - the plugin must read them from there.
        devices = {"sdb": {"size": "60.00 GB"}}
        mounts = [{"mount": "/var/lib/docker", "device": "/dev/sdb1"}]

        action_module, result = self._run(
            {"ansible_facts": {"devices": devices, "mounts": mounts}}
        )

        self.assertEqual(result, {"changed": False, "filesystems": []})
        action_module._execute_module.assert_called_once_with(
            module_name="find_filesystem_devices",
            module_args={
                "filesystem_list": [],
                "devices": devices,
                "mounts": mounts,
            },
            task_vars={"ansible_facts": {"devices": devices, "mounts": mounts}},
            tmp=None,
        )

    def test_run_falls_back_to_injected_vars(self):
        # With fact injection on, the top-level vars are used instead.
        devices = {"sdb": {"size": "60.00 GB"}}
        mounts = [{"mount": "/var/lib/docker", "device": "/dev/sdb1"}]

        action_module, result = self._run(
            {"ansible_devices": devices, "ansible_mounts": mounts}
        )

        self.assertEqual(result, {"changed": False, "filesystems": []})
        action_module._execute_module.assert_called_once_with(
            module_name="find_filesystem_devices",
            module_args={
                "filesystem_list": [],
                "devices": devices,
                "mounts": mounts,
            },
            task_vars={"ansible_devices": devices, "ansible_mounts": mounts},
            tmp=None,
        )


@unittest.skipUnless(
    sys.platform.startswith("linux") and shutil.which("findmnt"),
    "requires Linux and findmnt",
)
class TestFindmntIntegration(unittest.TestCase):
    def test_get_fstab_sources_with_findmnt(self):
        module = Mock()
        module.get_bin_path.side_effect = lambda command, required: shutil.which(command)

        def run_command(command, check_rc=False):
            result = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
            )
            if check_rc and result.returncode:
                raise ModuleFailure(result.stderr)
            return result.returncode, result.stdout, result.stderr

        module.run_command.side_effect = run_command

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mount_path = temp_path / "mount"
            mount_path.mkdir()
            fstab_path = temp_path / "fstab"
            fstab_path.write_text(
                f"/dev/null {mount_path} ext4 defaults 0 0\n",
                encoding="utf-8",
            )

            self.assertEqual(
                _get_fstab_sources(module, str(fstab_path), str(mount_path)),
                {"/dev/null"},
            )
