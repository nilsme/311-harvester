"""Download the entire NYC 311 dataset via the Socrata bulk CSV export."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

import requests

PROXY_ENV_VARS = {"http": "HTTP_PROXY", "https": "HTTPS_PROXY"}
APP_TOKEN = os.getenv("APP_TOKEN")
DATASET_ID = "erm2-nwe9"
BASE_DOMAIN = "data.cityofnewyork.us"
EXPORT_URL = f"https://{BASE_DOMAIN}/api/views/{DATASET_ID}/rows.csv?accessType=DOWNLOAD"
METADATA_URL = f"https://{BASE_DOMAIN}/api/views/{DATASET_ID}.json"
DEFAULT_OUTPUT_TEMPLATE = "311_all_{stamp}.csv"
DEFAULT_CHUNK_SIZE = 1 << 20  # 1 MiB
BYTES_PER_UNIT = 1024


def _build_session(app_token: str | None) -> requests.Session:
    """Create a requests session configured for the Socrata export.

    Args:
        app_token: API token read from the ``APP_TOKEN`` environment variable.

    Returns:
        requests.Session: Session with authentication headers and optional proxies.

    Raises:
        RuntimeError: If no API token is supplied.
    """
    if not app_token:
        raise RuntimeError(
            "Missing API token. Set the APP_TOKEN environment variable."
        )

    session = requests.Session()
    session.headers.update({"X-App-Token": app_token})

    proxies: dict[str, str] = {}
    for scheme, env_var in PROXY_ENV_VARS.items():
        value = os.getenv(env_var)
        if value:
            proxies[scheme] = value
    if proxies:
        session.proxies.update(proxies)

    return session


def _format_bytes(num_bytes: int) -> str:
    """Render a byte count as a human-friendly string.

    Args:
        num_bytes: Number of bytes to format.

    Returns:
        str: Human-readable value, e.g. ``"1.2 GB"``.
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < BYTES_PER_UNIT or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= BYTES_PER_UNIT
    return f"{size:.1f} PB"


def _fetch_last_update_stamp(session: requests.Session) -> str | None:
    """Return the dataset's last update timestamp formatted for filenames.

    Args:
        session: Configured HTTP session with authentication headers.

    Returns:
        str | None: Timestamp string (``YYYYMMDDHHMM``) if available, else ``None``.
    """
    response = session.get(METADATA_URL, timeout=30)
    response.raise_for_status()
    metadata = response.json()

    meta_section = metadata.get("metadata") or {}
    candidates = [
        metadata.get("rowsUpdatedAt"),
        metadata.get("dataUpdatedAt"),
        meta_section.get("dataUpdatedAt"),
        meta_section.get("rowsUpdatedAt"),
    ]
    updated_at = next((value for value in candidates if value), None)
    if updated_at is None:
        return None

    if isinstance(updated_at, int):
        updated_dt = datetime.fromtimestamp(updated_at, tz=timezone.utc)
    elif isinstance(updated_at, str):
        if updated_at.isdigit():
            updated_dt = datetime.fromtimestamp(int(updated_at), tz=timezone.utc)
        else:
            try:
                normalized = updated_at.replace("Z", "+00:00")
                updated_dt = datetime.fromisoformat(normalized)
            except ValueError:
                return None
    else:
        return None

    return updated_dt.strftime("%Y%m%d%H%M")


def _resolve_output_path(
    requested_path: str | None, session: requests.Session
) -> str:
    """Determine the filename to write the download to.

    Args:
        requested_path: Path supplied by the user, if any.
        session: Configured HTTP session used to query metadata.

    Returns:
        str: Absolute or relative path where the dataset will be saved.
    """
    if requested_path:
        return requested_path

    try:
        stamp = _fetch_last_update_stamp(session)
    except requests.RequestException:
        stamp = None

    if not stamp:
        stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M")

    return DEFAULT_OUTPUT_TEMPLATE.format(stamp=stamp)


def download_bulk_csv(
    output_path: str | None, chunk_size: int, verbose: bool
) -> None:
    """Stream the full dataset to disk via the bulk CSV export endpoint.

    Args:
        output_path: Destination file path where the CSV is written, or ``None`` to
            derive a timestamped name automatically.
        chunk_size: Number of bytes to read per iteration from the response stream.
        verbose: Whether to print incremental download progress to stdout.
    """
    session = _build_session(APP_TOKEN)
    resolved_output = _resolve_output_path(output_path, session)
    os.makedirs(os.path.dirname(resolved_output) or ".", exist_ok=True)

    with session.get(EXPORT_URL, stream=True, timeout=(10, 300)) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0

        with open(resolved_output, "wb") as handle:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                handle.write(chunk)
                downloaded += len(chunk)
                if verbose and total_size:
                    percent = downloaded / total_size * 100
                    print(
                        f"Downloaded {downloaded:,} bytes of {total_size:,} "
                        f"({percent:.1f}%).",
                        end="\r",
                    )
                elif verbose:
                    print(f"Downloaded {_format_bytes(downloaded)}", end="\r")

    if verbose:
        print()
    final_size = os.path.getsize(resolved_output)
    human_readable = _format_bytes(final_size)
    print(f"Saved {human_readable} to {resolved_output}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Destination file path for the CSV. If omitted, a timestamped name "
            "based on the dataset's last update (or current time) is used."
        ),
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Chunk size in bytes for streaming download (default: %(default)s).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress updates while downloading.",
    )
    args = parser.parse_args()

    try:
        download_bulk_csv(args.output, args.chunk_size, args.verbose)
    except requests.RequestException as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        sys.exit(1)
