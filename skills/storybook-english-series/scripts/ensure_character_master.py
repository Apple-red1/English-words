#!/usr/bin/env python3
"""Verify the approved character master and restore its exact bytes if needed."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Apple-red1/English-words"
MAX_DOWNLOAD_BYTES = 32 * 1024 * 1024


def read_manifest(path):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Character-master manifest must be a JSON object.")
    version = manifest.get("version", "")
    digest = manifest.get("sha256", "")
    filename = manifest.get("filename", "")
    if not re.fullmatch(r"v[1-9][0-9]*", version):
        raise ValueError("Manifest version must be v1, v2, etc.")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Manifest sha256 must be a lowercase SHA256 digest.")
    if filename != f"characters-{version}.png":
        raise ValueError("Manifest filename must match its character-master version.")
    if manifest.get("repository") != REPOSITORY:
        raise ValueError(f"Character master must come from {REPOSITORY}.")
    expected_path = f"skills/storybook-english-series/assets/characters/{filename}"
    if manifest.get("repository_path") != expected_path:
        raise ValueError("Manifest repository_path does not match the versioned master.")
    ref = manifest.get("git_ref", "")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", ref):
        raise ValueError("Manifest git_ref is missing or invalid.")
    expected_url = f"https://raw.githubusercontent.com/{REPOSITORY}/{ref}/{expected_path}"
    if manifest.get("raw_url") != expected_url:
        raise ValueError("Manifest raw_url must identify the official repository file.")
    return manifest


def hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_file(path, expected, failures):
    if not path.is_file():
        failures.append(f"Missing: {path}")
        return False
    try:
        actual = hash_file(path)
    except OSError as exc:
        failures.append(f"Cannot read {path}: {exc}")
        return False
    if actual != expected:
        failures.append(f"SHA256 mismatch for {path}: expected {expected}, got {actual}")
        return False
    return True


def restore_master(manifest, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        request = Request(manifest["raw_url"], headers={"User-Agent": "storybook-english-series/1"})
        with urlopen(request, timeout=30) as response:
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_url.hostname != "raw.githubusercontent.com":
                raise ValueError("Unexpected character-master download destination.")
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".part", delete=False) as handle:
                temporary = Path(handle.name)
                total = 0
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    total += len(block)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise ValueError("Character-master download exceeds 32 MiB.")
                    handle.write(block)
        actual = hash_file(temporary)
        if actual != manifest["sha256"]:
            raise ValueError(f"Downloaded master SHA256 mismatch: expected {manifest['sha256']}, got {actual}")
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=SKILL_ROOT / "assets/characters/manifest.json")
    parser.add_argument("--cache-dir", type=Path, help="Portable override for the cache root.")
    parser.add_argument("--offline", action="store_true", help="Check bundled/cache files without any network request.")
    parser.add_argument("--expected-version", help="Require the version already locked in the family project.")
    parser.add_argument("--expected-sha256", help="Require the hash already locked in the family project.")
    args = parser.parse_args()
    try:
        manifest_path = args.manifest.expanduser().resolve()
        manifest = read_manifest(manifest_path)
        if args.expected_version and args.expected_version != manifest["version"]:
            raise ValueError("Project master version differs from this manifest; use its archived manifest. Do not switch versions silently.")
        if args.expected_sha256 and args.expected_sha256 != manifest["sha256"]:
            raise ValueError("Project master SHA256 differs from this manifest. Do not replace or redraw the approved master.")
        cache_root = args.cache_dir or Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "storybook-english-series" / "characters"
        cached = cache_root.expanduser().resolve() / manifest["version"] / manifest["sha256"] / manifest["filename"]
        bundled = manifest_path.parent / manifest["filename"]
        failures = []
        if check_file(bundled, manifest["sha256"], failures):
            master, source = bundled, "bundled"
        elif check_file(cached, manifest["sha256"], failures):
            master, source = cached, "cache"
        elif args.offline:
            raise ValueError("No verified character master is available offline. " + "; ".join(failures))
        else:
            try:
                restore_master(manifest, cached)
            except (OSError, HTTPError, URLError, ValueError) as exc:
                raise ValueError("Cannot restore the approved character master. " + "; ".join(failures) + f"; download failed: {exc}. Stop image generation; do not generate a substitute.") from exc
            master, source = cached, "download"
        print(json.dumps({"ok": True, "path": str(master), "version": manifest["version"], "sha256": manifest["sha256"], "source": source, "raw_url": manifest["raw_url"]}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
