param(
    [string]$TestTarget = "backend/tests/test_api.py",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")

Push-Location $repoRoot
try {
    # Ensure backend package imports resolve inside tests.
    $env:PYTHONPATH = "$repoRoot"

    if (-not $env:DEV_TOKEN) { $env:DEV_TOKEN = "test-dev-token" }
    if (-not $env:FLASK_SECRET_KEY) { $env:FLASK_SECRET_KEY = "test-secret" }
    if (-not $env:WEBSITE_URL) { $env:WEBSITE_URL = "http://localhost:5173" }
    if (-not $env:VITE_API_URL) { $env:VITE_API_URL = "http://localhost:5000" }
    if (-not $env:VITE_GOOGLE_CLIENT_ID) { $env:VITE_GOOGLE_CLIENT_ID = "test-client-id" }
    if (-not $env:GOOGLE_CLIENT_SECRET) { $env:GOOGLE_CLIENT_SECRET = "test-client-secret" }

    $argsList = @($TestTarget)
    if ($PytestArgs) {
        $argsList += $PytestArgs
    }

    Write-Host "Running: pytest $($argsList -join ' ')" -ForegroundColor Cyan
    & pytest @argsList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
