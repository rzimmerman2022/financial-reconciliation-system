# Offline Assets Guide (Web Interface)

Run the web UI without internet access by serving JS libraries locally.

## What you need
Place these files under `static/vendor/` at the project root:
- tailwind.min.js
- alpine.min.js
- chart.umd.js

The app will use these when the environment variable `USE_LOCAL_ASSETS` is set to true.

## Enable local assets
- Windows PowerShell:
  - `$env:USE_LOCAL_ASSETS='true'`
- Windows CMD:
  - `set USE_LOCAL_ASSETS=true`
- Bash/Zsh (macOS/Linux):
  - `export USE_LOCAL_ASSETS=true`

Then start the web interface:
- `python bin/launch_web_interface`
- or `python -m src.review.web_interface`

## Where to download
- Tailwind CDN script (save as `tailwind.min.js`):
  - https://cdn.tailwindcss.com
- Alpine.js (save as `alpine.min.js`):
  - https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js
- Chart.js UMD (save as `chart.umd.js`):
  - https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.js

Tip: After downloading, place the files here:
```
static/
└── vendor/
    ├── tailwind.min.js
    ├── alpine.min.js
    └── chart.umd.js
```

## Verify integrity (optional)
Record checksums to track updates.
- PowerShell (Windows):
  - `Get-FileHash static\vendor\tailwind.min.js -Algorithm SHA256`
  - `Get-FileHash static\vendor\alpine.min.js -Algorithm SHA256`
  - `Get-FileHash static\vendor\chart.umd.js -Algorithm SHA256`
- Bash/Zsh (macOS/Linux):
  - `shasum -a 256 static/vendor/tailwind.min.js`
  - `shasum -a 256 static/vendor/alpine.min.js`
  - `shasum -a 256 static/vendor/chart.umd.js`

Store the resulting SHA256 values in a team-accessible location (e.g., docs/CURRENT_STATE.md) so updates are auditable.

## Troubleshooting
- If styles/scripts don’t load offline:
  - Confirm `USE_LOCAL_ASSETS` is set in the same shell you use to start the app.
  - Confirm the files exist with exact names in `static/vendor/`.
  - Check the browser console for 404s and ensure the Flask server is running.
