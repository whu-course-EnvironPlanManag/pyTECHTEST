"""
Tests for I/O module: YAML Loader, Excel Loader, and Excel Exporter.
"""

from pathlib import Path
import pytest
from pytechtest.io.yaml_loader import TechTestYAMLLoader
from pytechtest.io.excel_loader import TechTestExcelLoader
from pytechtest.io.excel_exporter import TechTestExcelExporter
from pytechtest.engines.full_engine import TechTestFullEngine


def test_yaml_loader(examples_dir: Path):
    yaml_path = examples_dir / "waste_heat_recovery.yaml"
    full_inp = TechTestYAMLLoader.load(yaml_path)
    assert full_inp.project.title != ""
    assert full_inp.functional_unit.reference_volume == 2.0


def test_excel_export_and_reload(examples_dir: Path, doe_excel_dir: Path, tmp_path: Path):
    template = doe_excel_dir / "TECHTEST 1.0 Blank Template.xlsx"
    if not template.exists():
        pytest.skip("Blank template not found on local path")

    # Load waste heat recovery model
    yaml_path = examples_dir / "waste_heat_recovery.yaml"
    engine = TechTestFullEngine.from_yaml(yaml_path)
    results = engine.run()

    # Export to tmp excel file
    out_xlsx = tmp_path / "exported_test.xlsx"
    exporter = TechTestExcelExporter(template_path=template)
    exporter.export(results, out_xlsx)
    assert out_xlsx.exists()

    # Verify reloading exported Excel
    loader = TechTestExcelLoader(out_xlsx)
    meta = loader.load_project_metadata()
    assert meta.title == results.project.title
