```yaml
---
# Mandatory parameters
win_scheduled_command_wrapper_password: "#{ENV['AO_DEFAULT_VAGRANT_PASSWORD']}",
win_scheduled_command: "& cmd.exe /c ver_err"

# Choices: limited, highest
win_scheduled_command_run_level: "highest"
```

Named pipe with ACL example
```powershell
$currentUser = ([Security.Principal.WindowsIdentity]::GetCurrent()).User
# $authUsers = New-Object -TypeName 'System.Security.Principal.SecurityIdentifier' -ArgumentList @([System.Security.Principal.WellKnownSidType]::AuthenticatedUserSid, $NULL)
# $everyone = New-Object -TypeName 'System.Security.Principal.SecurityIdentifier' -ArgumentList @([System.Security.Principal.WellKnownSidType]::WorldSid, $NULL)

$pipeSec = New-Object -TypeName System.IO.Pipes.PipeSecurity
$pipeAccessRule = New-Object -TypeName System.IO.Pipes.PipeAccessRule -ArgumentList @(
    $currentUser,
    # [System.IO.Pipes.PipeAccessRights]::ReadWrite,
    [System.IO.Pipes.PipeAccessRights]::FullControl,
    [System.Security.AccessControl.AccessControlType]::Allow
)
$pipeSec.AddAccessRule($pipeAccessRule)



# https://docs.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.-ctor?view=netframework-4.8#System_IO_Pipes_NamedPipeServerStream__ctor_System_String_System_IO_Pipes_PipeDirection_System_Int32_System_IO_Pipes_PipeTransmissionMode_System_IO_Pipes_PipeOptions_System_Int32_System_Int32_System_IO_Pipes_PipeSecurity_
$pipe = New-Object System.IO.Pipes.NamedPipeServerStream(
  $pipeName,
  [System.IO.Pipes.PipeDirection]::In,
  # maxNumberOfServerInstances
  1,
  [System.IO.Pipes.PipeTransmissionMode]::Byte,
  [System.IO.Pipes.PipeOptions]::None,
  # inBufferSize
  0,
  # outBufferSize
  0,
  # pipeSecurity
  $pipeSec
)
```