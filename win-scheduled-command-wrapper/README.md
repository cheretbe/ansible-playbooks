```yaml
---
# Mandatory parameters
win_scheduled_command_wrapper_password: "#{ENV['AO_DEFAULT_VAGRANT_PASSWORD']}",
win_scheduled_command: "& cmd.exe /c ver_err"

# Choices: limited, highest
win_scheduled_command_run_level: "highest"
```