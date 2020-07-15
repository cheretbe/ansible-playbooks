Set-StrictMode -Version Latest
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop

Write-Output "There you go"
"There you go" | Out-File -Append -FilePath "c:\test.txt"

throw "test exception"
