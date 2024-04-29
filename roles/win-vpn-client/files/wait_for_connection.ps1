Set-StrictMode -Version Latest
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop

Write-Output("Pinging host 'freegeoip.app'")
while ($NULL -eq (Test-Connection -ComputerName "freegeoip.app" -Count 2 -ErrorAction Continue)) {
  Start-Sleep -Seconds 1
}
