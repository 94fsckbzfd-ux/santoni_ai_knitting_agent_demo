param(
  [int]$Port = 8765
)

$connections = netstat -ano | Select-String ":$Port\s" | Select-String "LISTENING"
$processIds = @()

foreach ($connection in $connections) {
  $parts = ($connection.ToString() -split "\s+") | Where-Object { $_ -ne "" }
  if ($parts.Length -ge 5) {
    $processIds += [int]$parts[-1]
  }
}

$processIds = $processIds | Sort-Object -Unique

if (-not $processIds -or $processIds.Count -eq 0) {
  Write-Host "No process is listening on port $Port."
  exit 0
}

foreach ($processId in $processIds) {
  $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
  if ($null -eq $process) {
    continue
  }

  Write-Host "Stopping PID $processId ($($process.ProcessName)) on port $Port..."
  Stop-Process -Id $processId -Force
}

Write-Host "Done. Port $Port is clear."

