from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)

        validation_result, new_module_args = self.validate_argument_spec(
            argument_spec={
                'msg': {'type': 'str', 'required': True}
            }
        )

        self._display.warning(self._task.args.get("msg"))

        return result
