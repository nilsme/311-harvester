# Function Reference

This document summarizes the helper functions implemented in `download_all.py`.
Each entry mirrors the corresponding in-code docstring.

## `_build_session`

Create a requests session configured for the Socrata export.

Args:
  app_token: API token read from the `APP_TOKEN` environment variable.

Returns:
  requests.Session: Session with authentication headers and optional proxies.

Raises:
  RuntimeError: If no API token is supplied.

## `_format_bytes`

Render a byte count as a human-friendly string.

Args:
  num_bytes: Number of bytes to format.

Returns:
  str: Human-readable value, e.g. `"1.2 GB"`.

## `_fetch_last_update_stamp`

Return the dataset's last update timestamp formatted for filenames.

Args:
  session: Configured HTTP session with authentication headers.

Returns:
  str | None: Timestamp string (`YYYYMMDDHHMM`) if available, else `None`.

## `_resolve_output_path`

Determine the filename to write the download to.

Args:
  requested_path: Path supplied by the user, if any.
  session: Configured HTTP session used to query metadata.

Returns:
  str: Absolute or relative path where the dataset will be saved.

## `download_bulk_csv`

Stream the full dataset to disk via the bulk CSV export endpoint.

Args:
  output_path: Destination file path where the CSV is written, or `None` to
    derive a timestamped name automatically.
  chunk_size: Number of bytes to read per iteration from the response stream.
  verbose: Whether to print incremental download progress to stdout.
