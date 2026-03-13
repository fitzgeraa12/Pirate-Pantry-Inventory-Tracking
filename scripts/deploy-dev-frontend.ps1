Set-Location "$PSScriptRoot\..\frontend"
npm run build
npx wrangler pages deploy dist --project-name pirate-pantry-website --branch=dev
