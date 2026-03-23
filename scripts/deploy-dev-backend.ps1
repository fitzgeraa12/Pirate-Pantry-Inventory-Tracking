Set-Location "$PSScriptRoot\..\backend"
npx wrangler d1 migrations apply pirate-pantry-db-dev --remote --env dev
$env:PYTHONPATH = "."
python api/api.py
