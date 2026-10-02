"""Create a clean, downloadable ZIP of the project source, reports, and data."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".idea", ".vscode-test", "node_modules",
}
EXCLUDED_FILES = {".env", "secrets.toml"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".zip", ".sha256"}


def include_path(path: Path) -> bool:
    if path.is_symlink():
        return False
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.name in EXCLUDED_FILES or path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if path.name.startswith(".env."):
        return False
    if path.name.endswith(".egg-info"):
        return False
    if relative.parts and relative.parts[0] == "data":
        if relative.parts == ("data", "README.md"):
            return True
        if len(relative.parts) == 3 and relative.parts[1] == "raw":
            return relative.name in {"demo_sales.csv", "demo_products.csv"}
        if len(relative.parts) >= 2 and relative.parts[1] == "example_outputs":
            return path.is_file()
        return False
    return path.is_file()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(output: Path) -> tuple[int, str]:
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("The ZIP must be written outside the project folder.")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in ROOT.rglob("*") if include_path(path))
    if not files:
        raise ValueError("No project files were found to package.")
    package_name = ROOT.name
    manifest = [
        "Demand Forecasting & Inventory Optimization - package manifest",
        f"Generated (UTC): {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}",
        "Synthetic demo data and decisions are illustrative, not operational advice.",
        "",
        "Files:",
    ]
    manifest.extend(f"{sha256_file(path)}  {path.relative_to(ROOT).as_posix()}" for path in files)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            archive_name = f"{package_name}/{relative}"
            info = ZipInfo(archive_name, date_time=(2024, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
        manifest_info = ZipInfo(f"{package_name}/PACKAGE-MANIFEST.txt", date_time=(2024, 1, 1, 0, 0, 0))
        manifest_info.compress_type = ZIP_DEFLATED
        manifest_info.external_attr = 0o100644 << 16
        archive.writestr(
            manifest_info, "\n".join(manifest) + "\n",
            compress_type=ZIP_DEFLATED, compresslevel=9,
        )
    checksum = sha256_file(output)
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{checksum}  {output.name}\n", encoding="ascii"
    )
    return len(files) + 1, checksum


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT.parent / f"{ROOT.name}-Complete.zip",
        help="Output ZIP path (must be outside the project directory).",
    )
    args = parser.parse_args()
    file_count, checksum = build_archive(args.output)
    print(f"Created {args.output.resolve()}")
    print(f"Files (including package manifest): {file_count}")
    print(f"SHA-256: {checksum}")
    print(f"Checksum file: {args.output.resolve()}.sha256")


if __name__ == "__main__":
    main()
