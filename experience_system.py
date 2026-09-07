
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List
from trust_model import Other, Ego

class ExperienceFormat(Enum):
    TIDYBOT2=0
    LEROBOTV2=1
    LEROBOTV3=2

class Experience:
    experience_format: ExperienceFormat
    experiencer: List[Other]

    def __init__(self, path: Path):
        self.experience_format = Experience.detect_format(path)


    @staticmethod
    def detect_format(directory: Path):
        if not directory.is_dir():
            raise ValueError(f"Directory is not a directory, cannot detect experience format.")
