Set-StrictMode -Version Latest
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop


# $mmf = [System.IO.MemoryMappedFiles.MemoryMappedFile]::CreateNew("aaa-bbb-test", 5);

# $Stream = $mmf.CreateViewStream()

# $StreamWriter = New-Object System.IO.StreamWriter -ArgumentList $Stream

# $StreamWriter.Write("line1")
# $StreamWriter.Write("line2")

# $StreamWriter.Dispose()
# $Stream.Dispose()

# Write-Output "Press any key to continue..."
# [console]::ReadKey($TRUE) | Out-Null


# $mmf.Dispose()


# [System.IO.MemoryMappedFiles.MemoryMappedFile]::OpenExisting($Name);

# $pipeServer = New-Object -TypeName System.IO.Pipes.AnonymousPipeServerStream
# try {
#    Write-Output($pipeServer.GetClientHandleAsString())
# } finally {
#     $pipeServer.Dispose()
# }


$pipe = new-object System.IO.Pipes.NamedPipeServerStream("\\.\pipe\pips_spelling_server", [System.IO.Pipes.PipeDirection]::In)

$pipe.WaitForConnection()

$sr = new-object System.IO.StreamReader($pipe)

# while (($text = $sr.ReadLine()) -ne $null) 
Write-Host "Connected"
# $text = $sr.ReadLine()
while ($pipe.IsConnected)
{
  $pipe_data = $sr.ReadLine()
  if ($NULL -ne $pipe_data) {
    Write-Host $pipe_data.length
    $pipe_data | ConvertFrom-Json
  } #if
  # if ($NULL -eq $line) {
  #   Write-Host "NULL"
  # } else {
  #   Write-Host $line
  # } #if
  # $request = $text | ConvertFrom-Json
  # $candidates = $bktree.SearchFast($request.Request, $request.Distance)
  # $json = @{ 'Request'=$request.Request; 'Candidates'=$candidates; } | ConvertTo-Json -Depth 5 -Compress
  # $sw.WriteLine($json)
  # $sw.Flush()
  # $text = $null
  # $text = $sr.ReadLine()
  # Start-Sleep 1
}
Write-Host "Diconnected"

$sr.Dispose()