"""
Pytest configuration and shared fixtures for US DOE TECHTEST test suite.
"""

import sys
from pathlib import Path
import pytest

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from pytechtest import TechTestFullEngine, TechTestRapidEngine


@pytest.fixture
def project_root() -> Path:
    return BASE_DIR


@pytest.fixture
def examples_dir(project_root: Path) -> Path:
    return project_root / "examples"


@pytest.fixture
def data_dir(project_root: Path) -> Path:
    return project_root / "data"


@pytest.fixture
def doe_excel_dir(project_root: Path) -> Path:
    local_dir = project_root / "data" / "excel_templates"
    if local_dir.exists():
        return local_dir
    return Path("/Users/siqi/Documents/WHU_Office/课程教授/本科授课/Lecture_notes/环境规划与管理-第七讲20261015/TECHTEST_tool-Conceived-by-USDOE")
