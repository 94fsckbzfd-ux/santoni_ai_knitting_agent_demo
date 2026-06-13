[CmdletBinding()]
param(
    [switch]$InstallGitHooks,
    [switch]$Watch,
    [int]$WatchIntervalSeconds = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TargetName = "Medusa"
$SourceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..")).TrimEnd("\", "/")
$TargetRoot = Join-Path $SourceRoot $TargetName

$ExcludedDirectoryNames = @(
    ".git",
    ".codex_tmp",
    ".medusa_sync_tmp",
    $TargetName,
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build"
)

$ExcludedBinaryExtensions = @(
    ".7z",
    ".avi",
    ".bmp",
    ".doc",
    ".docx",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".pdf",
    ".png",
    ".pptx",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip"
)

$TextExtensions = @(
    ".bat",
    ".cmd",
    ".css",
    ".csv",
    ".example",
    ".gitignore",
    ".htm",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".svg",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml"
)

$TianpaiZh = [string]([char]0x5929) + [string]([char]0x6D3E)
$CompanyAZh = "A" + [string]([char]0x516C) + [string]([char]0x53F8)

function New-ReplacementPairs {
    $sourceSlash = $SourceRoot.Replace("\", "/")
    $sourceBackslash = $SourceRoot.Replace("/", "\")
    return @(
        @{ From = $sourceSlash; To = "Medusa workspace" },
        @{ From = $sourceBackslash; To = "Medusa workspace" },
        @{ From = "santoni-logo.png"; To = "medusa-logo.svg" },
        @{ From = "santoni-logo.svg"; To = "medusa-logo.svg" },
        @{ From = "Santoni Athena"; To = "Medusa" },
        @{ From = "Santoni's Athena"; To = "Medusa" },
        @{ From = "Santoni AI Knitting Agent"; To = "Medusa" },
        @{ From = "Santoni_AI_Knitting_Agent"; To = "Medusa" },
        @{ From = "SANTONI ATHENA"; To = "MEDUSA" },
        @{ From = "santoni athena"; To = "medusa" },
        @{ From = "AI Knitting Agent"; To = "Medusa" },
        @{ From = "ai-knitting-agent-demo"; To = "medusa" },
        @{ From = "Santoni (Shanghai) Knitting Machinery Co., Ltd"; To = "Medusa" },
        @{ From = "OneDrive - Santoni (Shanghai) Knitting Machinery Co., Ltd"; To = "OneDrive - Medusa" },
        @{ From = "SANTONI"; To = "MEDUSA" },
        @{ From = "Santoni"; To = "Medusa" },
        @{ From = "santoni"; To = "medusa" },
        @{ From = "TIANPAI"; To = "COMPANY_A" },
        @{ From = "TianpaiApsErpExportAdapter"; To = "CompanyAApsErpExportAdapter" },
        @{ From = "Tianpai"; To = "Company A" },
        @{ From = "tianpai"; To = "company_a" },
        @{ From = "SRC-TPI"; To = "SRC-COMPANY-A" },
        @{ From = "VOC-TPI"; To = "VOC-COMPANY-A" },
        @{ From = "TPI"; To = "COMPANY_A" },
        @{ From = "tpi"; To = "company_a" },
        @{ From = $TianpaiZh; To = $CompanyAZh },
        @{ From = "ATHENA"; To = "MEDUSA" },
        @{ From = "Athena"; To = "Medusa" },
        @{ From = "athena"; To = "medusa" },
        @{ From = "BELOTTI"; To = "COMPANY_B" },
        @{ From = "Belotti"; To = "Company B" },
        @{ From = "belotti"; To = "company_b" },
        @{ From = "MELOS"; To = "DATA_PARTNER" },
        @{ From = "Melos"; To = "Data Partner" },
        @{ From = "melos"; To = "data_partner" },
        @{ From = "AGNES"; To = "PRODUCT_OWNER" },
        @{ From = "Agnes"; To = "Product Owner" },
        @{ From = "agnes"; To = "product_owner" },
        @{ From = "JOEY"; To = "SERVICE_LEAD" },
        @{ From = "Joey"; To = "Service Lead" },
        @{ From = "joey"; To = "service_lead" }
    )
}

$ReplacementPairs = New-ReplacementPairs
$ForbiddenRegex = "Santoni|SANTONI|santoni|Tianpai|TIANPAI|tianpai|" +
    [regex]::Escape($TianpaiZh) +
    "|Athena|ATHENA|athena|Belotti|belotti|MELOS|Melos|melos|Agnes|AGNES|agnes|Joey|JOEY|joey|SRC-TPI|VOC-TPI"

function Convert-MedusaText {
    param([AllowNull()][string]$Value)

    if ($null -eq $Value) {
        return $null
    }

    $result = $Value
    foreach ($pair in $ReplacementPairs) {
        $result = $result.Replace([string]$pair.From, [string]$pair.To)
    }
    return $result
}

function Get-RelativeProjectPath {
    param([string]$FullPath)

    $full = [System.IO.Path]::GetFullPath($FullPath)
    if (-not $full.StartsWith($SourceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside source root: $FullPath"
    }

    return $full.Substring($SourceRoot.Length).TrimStart("\", "/")
}

function Test-IsExcludedPath {
    param([string]$FullPath)

    $relative = Get-RelativeProjectPath -FullPath $FullPath
    if ([string]::IsNullOrWhiteSpace($relative)) {
        return $false
    }

    $segments = $relative -split "[\\/]+"
    foreach ($segment in $segments) {
        if ($ExcludedDirectoryNames -contains $segment) {
            return $true
        }
    }
    return $false
}

function Test-IsExcludedFile {
    param([System.IO.FileInfo]$File)

    $relative = Get-RelativeProjectPath -FullPath $File.FullName
    $normalized = $relative.Replace("/", "\")
    $name = $File.Name
    $extension = $File.Extension.ToLowerInvariant()

    if ($normalized -ieq "tools\sync_medusa.ps1") {
        return $true
    }

    if ($name -eq ".env") {
        return $true
    }

    if ($name.StartsWith(".env.") -and $name -ne ".env.example") {
        return $true
    }

    if ($name.EndsWith(".log", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }

    if ($extension -eq ".pyc" -or $extension -eq ".pyo") {
        return $true
    }

    if ($normalized -match "(?i)src\\web_app\\santoni-logo\.(png|svg)$") {
        return $true
    }

    if ($ExcludedBinaryExtensions -contains $extension) {
        return $true
    }

    return $false
}

function Assert-SafeTarget {
    $sourceFull = [System.IO.Path]::GetFullPath($SourceRoot).TrimEnd("\", "/")
    $targetFull = [System.IO.Path]::GetFullPath($TargetRoot).TrimEnd("\", "/")
    $expectedPrefix = $sourceFull + [System.IO.Path]::DirectorySeparatorChar

    if ($targetFull -eq $sourceFull) {
        throw "Refusing to sync: target equals source."
    }

    if (-not $targetFull.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to sync: target is outside source root."
    }

    if ((Split-Path -Leaf $targetFull) -ne $TargetName) {
        throw "Refusing to sync: target leaf is not $TargetName."
    }
}

function Copy-SanitizedFile {
    param(
        [System.IO.FileInfo]$File,
        [string]$TempRoot
    )

    $relative = Get-RelativeProjectPath -FullPath $File.FullName
    $destinationRelative = Convert-MedusaText -Value $relative
    $destination = Join-Path $TempRoot $destinationRelative
    $destinationDirectory = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $destinationDirectory)) {
        New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
    }

    $extension = $File.Extension.ToLowerInvariant()
    if (($TextExtensions -contains $extension) -or ($File.Name -eq ".gitignore")) {
        $raw = [System.IO.File]::ReadAllText($File.FullName)
        $sanitized = Convert-MedusaText -Value $raw
        if ($destinationRelative.Replace("/", "\") -ieq "docs\tools\open_medusa_pmo.py") {
            $sanitized = $sanitized.Replace("PORT = 8788", "PORT = 8798")
        }
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($destination, $sanitized, $utf8NoBom)
    } else {
        Copy-Item -LiteralPath $File.FullName -Destination $destination -Force
    }
}

function New-MedusaLogo {
    param([string]$TempRoot)

    $logoDirectory = Join-Path $TempRoot "src\web_app"
    if (-not (Test-Path -LiteralPath $logoDirectory)) {
        New-Item -ItemType Directory -Force -Path $logoDirectory | Out-Null
    }

    $logoPath = Join-Path $logoDirectory "medusa-logo.svg"
    $logo = @'
<svg xmlns="http://www.w3.org/2000/svg" width="640" height="160" viewBox="0 0 640 160" role="img" aria-label="Medusa">
  <rect width="640" height="160" rx="24" fill="#101820"/>
  <path d="M82 106c24 0 44-20 44-44H98c0 9-7 16-16 16s-16-7-16-16H38c0 24 20 44 44 44Z" fill="#d8f05f"/>
  <path d="M82 38c-24 0-44 20-44 44h28c0-9 7-16 16-16s16 7 16 16h28c0-24-20-44-44-44Z" fill="#5fd6d8"/>
  <text x="164" y="98" fill="#f7f7f2" font-family="Segoe UI, Arial, sans-serif" font-size="56" font-weight="700" letter-spacing="0">MEDUSA</text>
</svg>
'@
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($logoPath, $logo, $utf8NoBom)
}

function New-MedusaReadme {
    param([string]$TempRoot)

    $readmePath = Join-Path $TempRoot "MEDUSA_SHADOW.md"
    $content = @'
# Medusa Shadow Project

This directory is generated by `tools/sync_medusa.ps1` from the working project.

The sync excludes source-control metadata, credentials, caches, logs, and binary media or office artifacts that cannot be deterministically text-sanitized.

Run from the source project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync_medusa.ps1
```

For file-save level mirroring during active editing:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync_medusa.ps1 -Watch
```
'@
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($readmePath, $content, $utf8NoBom)
}

function New-MedusaLauncher {
    param([string]$TempRoot)

    $launcherPath = Join-Path $TempRoot "Open_Medusa.bat"
    $content = @'
@echo off
setlocal

set "MEDUSA_ROOT=%~dp0"
set "MEDUSA_DEMO_PORT=8775"
cd /d "%MEDUSA_ROOT%"

if not exist "scripts\run_web_demo.py" (
  echo Missing scripts\run_web_demo.py.
  echo Please run tools\sync_medusa.ps1 from the source project, then try again.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $port = [int]$env:MEDUSA_DEMO_PORT; $url = 'http://127.0.0.1:' + $port + '/'; $python = Get-Command python -ErrorAction SilentlyContinue; if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }; if (-not $python) { Write-Host 'Python was not found. Please install Python or add it to PATH.'; exit 1 }; $listening = netstat -ano | Select-String (':' + $port + '\s') | Select-String 'LISTENING'; if ($env:MEDUSA_DEMO_SELF_TEST -eq '1') { $process = Start-Process -FilePath $python.Source -ArgumentList @('scripts\run_web_demo.py', [string]$port) -PassThru -WindowStyle Hidden; try { $deadline = (Get-Date).AddSeconds(8); do { Start-Sleep -Milliseconds 300; try { $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1; if ($response.StatusCode -eq 200) { Write-Host 'Medusa demo self-test passed:' $url; exit 0 } } catch {} } while ((Get-Date) -lt $deadline); Write-Host 'Medusa demo self-test failed:' $url; exit 1 } finally { if ($process -and -not $process.HasExited) { Stop-Process -Id $process.Id -Force } } }; if ($listening) { Write-Host 'Medusa demo is already running at' $url; Start-Process $url; Read-Host 'Press Enter to close this launcher window'; exit 0 }; Start-Process powershell -ArgumentList @('-NoProfile','-Command','Start-Sleep -Seconds 2; Start-Process ''' + $url + '''') -WindowStyle Hidden; Write-Host 'Starting Medusa demo at' $url; Write-Host 'Keep this window open while using Medusa. Press Ctrl+C to stop.'; & $python.Source 'scripts\run_web_demo.py' $port; exit $LASTEXITCODE }"
if errorlevel 1 (
  echo.
  echo Medusa demo launcher failed.
  pause
  exit /b 1
)

endlocal
'@
    Set-Content -LiteralPath $launcherPath -Value $content -NoNewline -Encoding Ascii
}

function Test-MedusaSanitization {
    $issues = New-Object System.Collections.Generic.List[string]
    $targetFull = [System.IO.Path]::GetFullPath($TargetRoot).TrimEnd("\", "/")

    Get-ChildItem -LiteralPath $TargetRoot -Recurse -Force | ForEach-Object {
        $relative = $_.FullName.Substring($targetFull.Length).TrimStart("\", "/")
        if ($relative -match $ForbiddenRegex) {
            $issues.Add("path: $relative")
        }

        if (-not $_.PSIsContainer) {
            $extension = $_.Extension.ToLowerInvariant()
            if (($TextExtensions -contains $extension) -or ($_.Name -eq ".gitignore")) {
                $matches = Select-String -LiteralPath $_.FullName -Pattern $ForbiddenRegex -ErrorAction SilentlyContinue
                foreach ($match in $matches) {
                    $issues.Add("content: ${relative}:$($match.LineNumber)")
                }
            }
        }
    }

    if ($issues.Count -gt 0) {
        $preview = ($issues | Select-Object -First 20) -join [Environment]::NewLine
        throw "Medusa sanitization check failed:$([Environment]::NewLine)$preview"
    }
}

function Invoke-MedusaSync {
    Assert-SafeTarget

    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("medusa_sync_" + [System.Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

    $copied = 0
    $skipped = 0

    try {
        Get-ChildItem -LiteralPath $SourceRoot -Recurse -Force -File | ForEach-Object {
            if ((Test-IsExcludedPath -FullPath $_.FullName) -or (Test-IsExcludedFile -File $_)) {
                $skipped += 1
            } else {
                Copy-SanitizedFile -File $_ -TempRoot $tempRoot
                $copied += 1
            }
        }

        New-MedusaLogo -TempRoot $tempRoot
        New-MedusaReadme -TempRoot $tempRoot
        New-MedusaLauncher -TempRoot $tempRoot

        if (Test-Path -LiteralPath $TargetRoot) {
            Remove-Item -LiteralPath $TargetRoot -Recurse -Force
        }

        Move-Item -LiteralPath $tempRoot -Destination $TargetRoot
        Test-MedusaSanitization

        Write-Host "Medusa sync complete."
        Write-Host "Target: $TargetRoot"
        Write-Host "Copied files: $copied"
        Write-Host "Skipped files: $skipped"
    } catch {
        if (Test-Path -LiteralPath $tempRoot) {
            Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
        throw
    }
}

function Install-MedusaGitHooks {
    $gitHooks = Join-Path $SourceRoot ".git\hooks"
    if (-not (Test-Path -LiteralPath $gitHooks)) {
        Write-Warning "Git hooks directory not found; skipping hook installation."
        return
    }

    $hookBody = "#!/bin/sh`n" +
        "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./tools/sync_medusa.ps1 >/dev/null 2>&1 || true`n"

    foreach ($hookName in @("post-commit", "post-merge", "post-checkout")) {
        $hookPath = Join-Path $gitHooks $hookName
        Set-Content -LiteralPath $hookPath -Value $hookBody -NoNewline -Encoding Ascii
    }

    Write-Host "Installed Medusa Git hooks: post-commit, post-merge, post-checkout"
}

function Get-SourceFingerprint {
    $builder = New-Object System.Text.StringBuilder
    Get-ChildItem -LiteralPath $SourceRoot -Recurse -Force -File | ForEach-Object {
        if (-not ((Test-IsExcludedPath -FullPath $_.FullName) -or (Test-IsExcludedFile -File $_))) {
            $relative = Get-RelativeProjectPath -FullPath $_.FullName
            [void]$builder.AppendLine("$relative|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)")
        }
    }
    return $builder.ToString()
}

if ($WatchIntervalSeconds -lt 2) {
    throw "WatchIntervalSeconds must be at least 2."
}

Invoke-MedusaSync

if ($InstallGitHooks) {
    Install-MedusaGitHooks
}

if ($Watch) {
    Write-Host "Watching source project for changes. Press Ctrl+C to stop."
    $lastFingerprint = Get-SourceFingerprint
    while ($true) {
        Start-Sleep -Seconds $WatchIntervalSeconds
        $currentFingerprint = Get-SourceFingerprint
        if ($currentFingerprint -ne $lastFingerprint) {
            Invoke-MedusaSync
            $lastFingerprint = Get-SourceFingerprint
        }
    }
}
