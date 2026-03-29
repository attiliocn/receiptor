from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.cli
def test_cli_success_creates_csv(repo_root: Path, fixtures_dir: Path, tmp_path: Path) -> None:
    script_path = repo_root / "receiptor" / "receiptor.py"
    pdf_path = fixtures_dir / "pdfs" / "paraiso_baseline.pdf"
    output_path = tmp_path / "cli-output.csv"

    result = subprocess.run(
        [sys.executable, str(script_path), str(pdf_path), "-o", str(output_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert output_path.exists()


@pytest.mark.cli
def test_cli_missing_input_file(repo_root: Path, tmp_path: Path) -> None:
    script_path = repo_root / "receiptor" / "receiptor.py"
    missing_pdf = tmp_path / "missing.pdf"

    result = subprocess.run(
        [sys.executable, str(script_path), str(missing_pdf)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Input file not found" in result.stderr


@pytest.mark.cli
def test_cli_rejects_non_pdf_input(repo_root: Path, tmp_path: Path) -> None:
    script_path = repo_root / "receiptor" / "receiptor.py"
    txt_input = tmp_path / "receipt.txt"
    txt_input.write_text("not a pdf", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(script_path), str(txt_input)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "must be a PDF file" in result.stderr


@pytest.mark.cli
def test_cli_quiet_hides_startup_banner(repo_root: Path, fixtures_dir: Path, tmp_path: Path) -> None:
    script_path = repo_root / "receiptor" / "receiptor.py"
    pdf_path = fixtures_dir / "pdfs" / "paraiso_baseline.pdf"
    output_path = tmp_path / "quiet-output.csv"

    result = subprocess.run(
        [sys.executable, str(script_path), str(pdf_path), "-o", str(output_path), "--quiet"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Starting receipt extraction script" not in result.stdout
