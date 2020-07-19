Set-StrictMode -Version Latest
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop


# $mmf = [System.IO.MemoryMappedFiles.MemoryMappedFile]::OpenExisting("aaa-bbb-test");

# $Stream = $mmf.CreateViewStream()

# $StreamReader = New-Object System.IO.StreamReader -ArgumentList $Stream

# $test = $StreamReader.ReadToEnd().Replace("`0", "")
# $StreamReader.Dispose()
# $Stream.Dispose()

# $mmf.Dispose()

# write-output($test)


# # [System.IO.MemoryMappedFiles.MemoryMappedFile]::OpenExisting($Name);

# $pipe = New-Object -TypeName System.IO.Pipes.NamedPipeClientStream -ArgumentList @(
#     ".",  # localhost
#     "\\.\pipe\pips_spelling_server",
#     [System.IO.Pipes.PipeDirection]::Out #,
#     # [System.IO.Pipes.PipeOptions]::None,
#     # [System.Security.Principal.TokenImpersonationLevel]::Anonymous
# )

# try {
#     $pipe.Connect()
#     $sw = New-Object System.IO.StreamWriter($pipe)
#     $sw.WriteLine("aaa")
#     $sw.Flush()
#     Start-Sleep 5
#     $sw.WriteLine("bbb")
#     $sw.Flush()
# } finally {
#     $pipe.Close()
# }


# https://devblogs.microsoft.com/powershell/how-objects-are-sent-to-and-from-remote-sessions/
# https://stackoverflow.com/questions/41807392/deserialized-object-type-issues-specifically-with-powershell-5-classes-and-imp
# https://github.com/PowerShell/PowerShell/issues/3173
# https://asaconsultant.blogspot.com/2017/02/serialize-data-with-powershell.html
# https://stackoverflow.com/questions/18747942/how-to-use-a-powerhsell-serialized-object

function PipeOutput {
[CmdletBinding()]
param(
  [Parameter(Mandatory=$TRUE,ValueFromPipeline=$TRUE,ValueFromPipelinebyPropertyName=$FALSE)] $inputObject
)
  Begin {
    $pipe = New-Object -TypeName System.IO.Pipes.NamedPipeClientStream -ArgumentList @(
      ".",  # localhost
      "\\.\pipe\pips_spelling_server",
      [System.IO.Pipes.PipeDirection]::Out
    )
    $pipe_writer = New-Object System.IO.StreamWriter($pipe)
    $pipe.Connect()
  }

  Process {
    $dummy = ($inputObject | ConvertTo-Json -Compress)
    Write-Host ($dummy.length)
    $pipe_writer.Write($dummy)
    # $pipe_writer.Write(($inputObject | ConvertTo-Json -Compress))
    # $pipe_writer.Flush()
    Write-Host ($inputObject.GetType().FullName) -ForeColor Cyan
    $inputObject
  }

  End {
    $pipe.Close()
  }
}

. {
  Get-childitem
} | PipeOutput
