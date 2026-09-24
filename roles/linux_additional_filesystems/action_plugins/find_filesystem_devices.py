from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        # Ensure task_vars is not None
        task_vars = task_vars or {}

        # The block-device inventory and mount table live under ansible_facts.
        # This repo runs with ANSIBLE_INJECT_FACT_VARS=false, so the top-level
        # ansible_devices/ansible_mounts vars are absent - read ansible_facts
        # first and fall back to the injected names for projects that keep
        # injection on.
        facts = task_vars.get("ansible_facts", {})
        ansible_devices = facts.get("devices") or task_vars.get("ansible_devices", {})
        ansible_mounts = facts.get("mounts") or task_vars.get("ansible_mounts", [])

        # Pass all user args, but override/add devices
        module_args = self._task.args.copy()
        module_args["devices"] = ansible_devices
        module_args["mounts"] = ansible_mounts

        # Call the underlying module with updated args
        result = self._execute_module(
            module_name="find_filesystem_devices", module_args=module_args, task_vars=task_vars, tmp=tmp
        )
        return result
