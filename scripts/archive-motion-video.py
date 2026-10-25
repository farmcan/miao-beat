#!/usr/bin/env python3
"""Preserve an authorized motion source before previewing or slicing it.

Raw media stays under ignored assets-source/. Signed URLs are read from stdin,
never written to metadata, command arguments, or error messages.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 128 * 1024 * 1024


def archive(args):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,63}", args.name):
        raise ValueError("Use a short lowercase take name, with digits/hyphens only")
    parent = ROOT / "assets-source/motion"
    target = parent / args.name
    if target.exists():
        raise ValueError("That take already exists; use a new name to preserve it")
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".incoming-", dir=parent) as temporary:
        stage = Path(temporary) / "take"
        stage.mkdir()
        source = stage / "source.mp4"
        if args.file:
            if not args.file.is_file() or not 0 < args.file.stat().st_size <= MAX_BYTES:
                raise ValueError("Local video is missing, empty, or exceeds 128 MiB")
            shutil.copyfile(args.file, source)
        else:
            url = sys.stdin.read().strip()
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("Expected one HTTPS download URL on stdin")
            request = Request(url, headers={"User-Agent": "MiaoBeat-MotionArchive/1.0"})
            with urlopen(request, timeout=30) as response, source.open("wb") as output:
                if int(response.headers.get("Content-Length", "0")) > MAX_BYTES:
                    raise ValueError("Download exceeds 128 MiB")
                size = 0
                while chunk := response.read(256 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise ValueError("Download exceeds 128 MiB")
                    output.write(chunk)
            if not size:
                raise ValueError("Download was empty")
        metadata = {
            "take": args.name,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "source_url_saved": False,
            "file": "source.mp4",
            "bytes": source.stat().st_size,
            "sha256": hashlib.file_digest(source.open("rb"), "sha256").hexdigest(),
            "validated": False,
        }
        (stage / "source.json").write_text(json.dumps(metadata, indent=2) + "\n")
        stage.rename(target)
    # Retain the complete original even if a later probe/codec check fails.
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(target / "source.mp4")],
            capture_output=True, text=True, check=True, timeout=30,
        )
        data = json.loads(probe.stdout)
        video = next(stream for stream in data["streams"] if stream.get("codec_type") == "video")
        duration = float(data["format"]["duration"])
        if not math.isfinite(duration) or duration <= 0 or not video.get("width") or not video.get("height"):
            raise ValueError("Invalid video metadata")
        if "mp4" not in data["format"].get("format_name", ""):
            raise ValueError("Expected an MP4 source")
        metadata.update({
            "validated": True,
            "duration_seconds": duration,
            "width": video["width"],
            "height": video["height"],
            "frame_rate": video.get("avg_frame_rate"),
            "codec": video.get("codec_name"),
            "has_audio": any(stream.get("codec_type") == "audio" for stream in data["streams"]),
        })
        (target / "source.json").write_text(json.dumps(metadata, indent=2) + "\n")
    except Exception as error:
        raise ValueError("Original preserved at " + str(target.relative_to(ROOT)) + "; video validation failed (" + type(error).__name__ + ")") from None
    print(json.dumps({"archive": str(target.relative_to(ROOT)), **metadata}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--file", type=Path)
    inputs.add_argument("--url-stdin", action="store_true")
    arguments = parser.parse_args()
    try:
        archive(arguments)
    except HTTPError as error:
        print("Archive failed: source returned HTTP " + str(error.code) + "; URL was not saved", file=sys.stderr)
        sys.exit(1)
    except (URLError, TimeoutError) as error:
        print("Archive failed: source network unavailable (" + type(error).__name__ + "); URL was not saved", file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(str(error) if isinstance(error, ValueError) else "Archive failed: " + type(error).__name__, file=sys.stderr)
        sys.exit(1)
