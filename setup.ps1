$ErrorActionPreference = "Stop"
$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $rootPath

$pythonCommand = $null
$pythonPrefix = @()
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($version in @("-3.11", "-3.12")) {
        & py $version --version *> $null
        if ($LASTEXITCODE -eq 0) { $pythonCommand = "py"; $pythonPrefix = @($version); break }
    }
}
if (-not $pythonCommand) {
    if (Test-Path -LiteralPath $bundledPython) { $pythonCommand = $bundledPython }
}
if (-not $pythonCommand) { throw "Python 3.11 or 3.12 was not found. Install one, then rerun setup.ps1." }

$workPath = Join-Path $rootPath "work"
$packagesPath = Join-Path $workPath "python-packages"
$tempPath = Join-Path $workPath "tmp"
New-Item -ItemType Directory -Force -Path $packagesPath, $tempPath | Out-Null
$env:TEMP = $tempPath
$env:TMP = $tempPath

# Create and use the repository environment. The bundled interpreter is only a
# bootstrap fallback when Windows has no Python launcher installed.
$venvPython = Join-Path $rootPath ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $pythonCommand @pythonPrefix -m venv (Join-Path $rootPath ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create the repository .venv." }
}

$dependencyCheck = "from importlib.metadata import version; expected={'pytest':'9.2.0','pydantic':'2.14.1','networkx':'3.7','numpy':'2.3.5','pandas':'3.0.1','scipy':'1.18.1','typer':'0.27.3','PyYAML':'6.0.3'}; assert all(version(name)==value for name,value in expected.items())"
& $venvPython -c $dependencyCheck *> $null
if ($LASTEXITCODE -ne 0) {
    # An extracted, pinned package cache is included in the workspace. Copy it
    # into .venv so tests and CLI use only the repository interpreter.
    if ((Test-Path -LiteralPath $packagesPath) -and (Test-Path -LiteralPath (Join-Path $packagesPath "pytest"))) {
        robocopy $packagesPath (Join-Path $rootPath ".venv\Lib\site-packages") /E /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null
        if ($LASTEXITCODE -gt 7) { throw "Could not populate .venv from the local pinned package cache." }
    }
    & $venvPython -c $dependencyCheck *> $null
    if ($LASTEXITCODE -ne 0) {
        # The workspace cache intentionally contains only a subset of binary
        # wheels. Seed the missing pinned numerical/model packages from the
        # local runtime package cache, then execute tests exclusively via .venv.
        $bundleSitePackages = Join-Path (Split-Path -Parent $bundledPython) "Lib\site-packages"
        $bundlePackageNames = @("annotated_types", "annotated_types-0.8.0.dist-info", "numpy", "numpy-2.3.5.dist-info", "numpy.libs", "pandas", "pandas-3.0.1.dist-info", "pandas.libs", "pydantic", "pydantic-2.14.1.dist-info", "pydantic_core", "pydantic_core-2.50.1.dist-info", "typing_extensions.py", "typing_extensions-4.16.0.dist-info", "typing_inspection", "typing_inspection-0.4.4.dist-info", "dateutil", "python_dateutil-2.9.0.post0.dist-info", "six.py", "six-1.17.0.dist-info", "tzdata", "tzdata-2025.3.dist-info")
        if (Test-Path -LiteralPath $bundleSitePackages) {
            $venvPackages = Join-Path $rootPath ".venv\Lib\site-packages"
            foreach ($packageName in $bundlePackageNames) {
                $sourcePackage = Join-Path $bundleSitePackages $packageName
                if (-not (Test-Path -LiteralPath $sourcePackage)) { continue }
                $targetPackage = Join-Path $venvPackages $packageName
                if ((Get-Item -LiteralPath $sourcePackage).PSIsContainer) {
                    robocopy $sourcePackage $targetPackage /E /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null
                    if ($LASTEXITCODE -gt 7) { throw "Could not copy .venv dependency $packageName." }
                } else {
                    Copy-Item -LiteralPath $sourcePackage -Destination $targetPackage -Force
                }
            }
        }
    }
    & $venvPython -c $dependencyCheck *> $null
    if ($LASTEXITCODE -ne 0) {
        & $venvPython -m ensurepip --upgrade *> $null
        & $venvPython -m pip install --disable-pip-version-check -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw "Pinned dependencies are unavailable. Check network access or populate work/python-packages." }
    }
}
& $venvPython -m pytest --basetemp (Join-Path $workPath "pytest-run-temp")
if ($LASTEXITCODE -ne 0) { throw "Pytest failed." }
& $venvPython -m inquest.cli doctor --config config.yaml
if ($LASTEXITCODE -ne 0) { throw "inquest doctor failed." }
Write-Host "Pinned dependencies in .venv, pytest, and inquest doctor completed successfully."
