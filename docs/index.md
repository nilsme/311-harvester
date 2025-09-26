# NYC 311 Harvester

This project provides a command-line utility for downloading the full NYC 311
service request dataset (dataset id `erm2-nwe9`) from the NYC OpenData Portal
using the official bulk CSV export endpoint. The script focuses on a reliable,
single-request download flow while adding a few quality-of-life improvements:

- Automatic discovery of dataset metadata so that generated files include the
  last update timestamp (or current UTC time when not available).
- Support for authentication via `APP_TOKEN` and optional HTTP/HTTPS proxies
  through standard environment variables.
- Progress feedback during long-running downloads, with optional verbose mode
  for detailed tracing.

The repository exposes a single script, `download_all.py`, plus a handful of
internal helpers documented in `docs/functions.md`.
