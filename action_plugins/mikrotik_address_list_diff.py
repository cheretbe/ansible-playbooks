from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)

        existing_records = self._task.args.get("existing_records", None)
        if existing_records is None:
            raise AnsibleActionFail("'existing_records' parameter needs to be provided")

        new_ips = self._task.args.get("new_ips", None)
        if new_ips is None:
            raise AnsibleActionFail("'new_ips' parameter needs to be provided")

        result["ids_to_delete"] = []
        result["ips_to_add"] = []

        for record in existing_records:
            if not next((ip for ip in new_ips if ip["address"] == record["address"]), None):
                result["ids_to_delete"].append(record[".id"])

        for ip in new_ips:
            if not next((record for record in existing_records if record["address"] == ip["address"]), None):
                result["ips_to_add"].append(ip)

        return result
