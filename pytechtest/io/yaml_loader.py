"""
YAML Loader for TECHTEST 1.0 configurations.
"""

from pathlib import Path
from typing import Union, Dict, Any
import yaml
from pytechtest.models.full_entry_input import FullEntryInput
from pytechtest.models.rapid_entry_input import RapidEntryInput


def load_yaml_config(path: Union[str, Path]) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_full_input_from_yaml(path: Union[str, Path]) -> FullEntryInput:
    data = load_yaml_config(path)
    return FullEntryInput(**data)


def load_rapid_input_from_yaml(path: Union[str, Path]) -> RapidEntryInput:
    data = load_yaml_config(path)
    return RapidEntryInput(**data)


class TechTestYAMLLoader:
    """Unified YAML Loader for Full and Rapid inputs."""

    @staticmethod
    def load(path: Union[str, Path]) -> FullEntryInput:
        return load_full_input_from_yaml(path)

    @staticmethod
    def load_full(path: Union[str, Path]) -> FullEntryInput:
        return load_full_input_from_yaml(path)

    @staticmethod
    def load_rapid(path: Union[str, Path]) -> RapidEntryInput:
        return load_rapid_input_from_yaml(path)

