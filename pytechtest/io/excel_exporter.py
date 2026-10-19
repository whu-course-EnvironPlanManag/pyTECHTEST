"""
Excel Exporter for US DOE TECHTEST 1.0.
Takes TechTestResults or FullEntryInput and populates a pristine blank template workbook.
"""

from pathlib import Path
import shutil
from typing import Union, Optional
import openpyxl
from pytechtest.models.results import TechTestResults

# Path to the source blank template
_DEFAULT_TEMPLATE = Path("/Users/siqi/Documents/WHU_Office/课程教授/本科授课/Lecture_notes/环境规划与管理-第七讲20261015/TECHTEST_tool-Conceived-by-USDOE/TECHTEST 1.0 Blank Template.xlsx")


class TechTestExcelExporter:
    """Exports Python evaluation results into official US DOE TECHTEST Excel template."""

    def __init__(self, template_path: Optional[Union[str, Path]] = None):
        self.template_path = Path(template_path) if template_path else _DEFAULT_TEMPLATE
        if not self.template_path.exists():
            raise FileNotFoundError(f"Blank template not found at {self.template_path}")

    def export(self, results: TechTestResults, output_path: Union[str, Path]):
        """Populate results into the Excel template and save to output_path."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.template_path, out_p)

        wb = openpyxl.load_workbook(str(out_p))

        # 1. Project Basics
        if "Project Basics & Benchmarks" in wb.sheetnames:
            ws_pb = wb["Project Basics & Benchmarks"]
            ws_pb["C7"] = results.project.title
            ws_pb["C8"] = results.project.lead_organization
            ws_pb["C9"] = results.project.partners
            ws_pb["C10"] = results.project.principal_investigator
            ws_pb["C11"] = results.project.pi_organization
            ws_pb["C12"] = results.project.technology_manager
            ws_pb["C13"] = results.project.start_date
            ws_pb["C14"] = results.project.end_date
            ws_pb["C15"] = results.project.funding_mechanism
            ws_pb["C24"] = results.market.generic_end_use_product

        # 2. Market
        if "Market" in wb.sheetnames:
            ws_mkt = wb["Market"]
            ws_mkt["C8"] = results.market.annual_us_market_volume
            ws_mkt["D8"] = results.market.market_units
            ws_mkt["F20"] = results.market.target_penetration_fraction

        # 3. Functional Unit
        if "Functional Unit" in wb.sheetnames:
            ws_fu = wb["Functional Unit"]
            ws_fu["D20"] = results.functional_unit.reference_volume
            ws_fu["E20"] = results.functional_unit.reference_volume_unit
            ws_fu["G20"] = results.new_technology.product_name
            ws_fu["D29"] = results.functional_unit.reference_volume * results.functional_unit.equivalence_ratio
            ws_fu["G29"] = results.commercial_benchmark.product_name

        # 4. CapEx
        if "CapEx" in wb.sheetnames:
            ws_cap = wb["CapEx"]
            ws_cap["C15"] = results.new_technology.facility_production_volume
            ws_cap["K15"] = results.commercial_benchmark.facility_production_volume

        wb.save(str(out_p))
