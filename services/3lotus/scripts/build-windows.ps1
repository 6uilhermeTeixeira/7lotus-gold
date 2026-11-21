$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectRoot

py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --name 2lotus-runner --onedir --paths . runner_entry.py
& "$projectRoot\dist\2lotus-runner\2lotus-runner.exe" --check

$packageRoot = Join-Path $projectRoot "package\2lotus-runner"
New-Item -ItemType Directory -Force -Path $packageRoot | Out-Null
Copy-Item -Path "$projectRoot\dist\2lotus-runner\*" -Destination $packageRoot -Recurse -Force
foreach ($directory in @("strategies", "mt5", "scripts")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $packageRoot $directory) | Out-Null
}
Copy-Item -Path "$projectRoot\strategies\*" -Destination (Join-Path $packageRoot "strategies") -Recurse -Force
Copy-Item -Path "$projectRoot\mt5\LotusRunnerBridge.mq5" -Destination (Join-Path $packageRoot "mt5") -Force
Copy-Item -Path "$projectRoot\scripts\install.ps1" -Destination (Join-Path $packageRoot "scripts") -Force
Copy-Item -Path "$projectRoot\README.md" -Destination $packageRoot -Force

$archive = Join-Path $projectRoot "package\2lotus-runner-windows-x64.zip"
if (Test-Path $archive) { Remove-Item $archive }
Compress-Archive -Path $packageRoot -DestinationPath $archive
Write-Host "Package ready: $archive"
