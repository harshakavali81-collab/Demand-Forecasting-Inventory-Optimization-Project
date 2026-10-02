from pathlib import Path
from zipfile import ZipFile

from scripts.package_project import ROOT, build_archive


def test_packager_includes_deliverables_and_excludes_local_state(tmp_path: Path):
    output = tmp_path / "project.zip"
    file_count, checksum = build_archive(output)
    assert file_count > 20
    assert len(checksum) == 64
    with ZipFile(output) as archive:
        names = archive.namelist()
    assert f"{ROOT.name}/README.md" in names
    assert f"{ROOT.name}/data/raw/demo_sales.csv" in names
    assert f"{ROOT.name}/data/example_outputs/forecast.csv" in names
    assert f"{ROOT.name}/reports/Project_Report.pdf" in names
    assert f"{ROOT.name}/reports/Project_Presentation.pptx" in names
    assert f"{ROOT.name}/PACKAGE-MANIFEST.txt" in names
    assert not any("/.git/" in name or "/.venv/" in name or "/__pycache__/" in name for name in names)
    assert not any(name.endswith("/.env") or "/secrets.toml" in name for name in names)
    assert not any("/data/processed/" in name for name in names)
    assert output.with_suffix(".zip.sha256").is_file()


def test_packager_refuses_output_inside_repository(tmp_path: Path):
    output = ROOT / "nested-project.zip"
    try:
        build_archive(output)
    except ValueError as error:
        assert "outside the project folder" in str(error)
    else:
        raise AssertionError("Expected the output path guard to fail.")
