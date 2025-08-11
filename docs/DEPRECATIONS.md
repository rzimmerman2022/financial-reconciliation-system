# Deprecations and Archived Items (v6.0.0)

This document lists deprecated commands, scripts, and paths, with their replacements.

## Deprecated Commands/Paths

- Web interface launcher:
  - Old: `python src/web/reconcile_web.py`
  - New: `python bin/launch_web_interface` or `python -m src.review.web_interface`

- Excel export:
  - Old: `python src/scripts/export_to_excel.py`
  - New: `python bin/export-excel`

- GUI launcher:
  - Old: `python launch_gui.py`
  - New: `python launch_ultra_premium_gui.py`

## Archived or Redirected

- Top-level `description_decoder.py` was a stub. It now shims to `src/core/description_decoder.py`.
- Legacy dashboards and experimental GUIs are maintained under `archive/` where applicable.

## Notes

- The web interface now supports an optional `USE_LOCAL_ASSETS=true` environment variable to use local JS assets under `static/vendor/`.
- Paths and commands in README/QUICKSTART were updated to reflect these changes.
