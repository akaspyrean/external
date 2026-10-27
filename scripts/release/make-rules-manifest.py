#!/usr/bin/env python3
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_VERSION = 1


def hash_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def collect_files(repo_dir: Path) -> list[Path]:
    patterns = ["rules/*.yaml", "geodata/*"]
    found: dict[str, Path] = {}
    for pattern in patterns:
        for path in repo_dir.glob(pattern):
            if not path.is_file():
                continue
            if path.name.startswith("."):
                continue
            rel = path.relative_to(repo_dir).as_posix()
            found[rel] = path
    return [found[key] for key in sorted(found)]


def build_manifest(repo_dir: Path, commit: str) -> dict:
    files = []
    for path in collect_files(repo_dir):
        rel = path.relative_to(repo_dir).as_posix()
        size, sha256 = hash_file(path)
        files.append({"path": rel, "size": size, "sha256": sha256})

    return {
        "version": MANIFEST_VERSION,
        "commit": commit,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "count": len(files),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate rules-manifest.json")
    parser.add_argument("--repo-dir", default=".", help="repository root")
    parser.add_argument("--commit", default="", help="commit hash to record")
    parser.add_argument("--out", default="rules-manifest.json", help="output file")
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir).resolve()
    manifest = build_manifest(repo_dir, args.commit)

    out_path = Path(args.out)
    out_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out_path} with {manifest['count']} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
