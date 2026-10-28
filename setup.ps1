$ErrorActionPreference = "Stop"
$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $rootPath

$pythonCommand = $null
$pythonPrefix = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($version in @("-3.11", "-3.12")) {
        & py $version --version *> $null
        if ($LASTEXITCODE -eq 0) { $pythonCommand = "py"; $pythonPrefix = @($version); break }
    }
}
if (-not $pythonCommand) {
    $bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $bundledPython) { $pythonCommand = $bundledPython }
}
if (-not $pythonCommand) { throw "Python 3.11 or 3.12 was not found. Install one, then rerun setup.ps1." }

$workPath = Join-Path $rootPath "work"
$packagesPath = Join-Path $workPath "python-packages"
$tempPath = Join-Path $workPath "tmp"
New-Item -ItemType Directory -Force -Path $packagesPath, $tempPath | Out-Null
$env:PYTHONPATH = $packagesPath
$env:TEMP = $tempPath
$env:TMP = $tempPath

# Reuse an already provisioned workspace package cache (useful offline). If it
# is incomplete, install the pinned requirements into that local cache.
$dependencyCheck = "from importlib.metadata import version; expected={'pytest':'9.2.0','pydantic':'2.14.1','networkx':'3.7','numpy':'2.3.5','pandas':'3.0.1','scipy':'1.18.1','typer':'0.27.3','PyYAML':'6.0.3'}; assert all(version(name)==value for name,value in expected.items())"
& $pythonCommand @pythonPrefix -c $dependencyCheck *> $null
if ($LASTEXITCODE -ne 0) {
    & $pythonCommand @pythonPrefix -m pip install --disable-pip-version-check --target $packagesPath -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Pinned dependencies are unavailable. Check network access or install requirements.txt into work/python-packages." }
}
& $pythonCommand @pythonPrefix -m pytest --basetemp (Join-Path $workPath "pytest-run-temp")
if ($LASTEXITCODE -ne 0) { throw "Pytest failed." }
& $pythonCommand @pythonPrefix -m inquest.cli doctor --config config.yaml
if ($LASTEXITCODE -ne 0) { throw "inquest doctor failed." }
Write-Host "Dependencies, pytest, and inquest doctor completed successfully."
