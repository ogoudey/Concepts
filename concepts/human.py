from .compute_environment import ComputeEnvironment
from typing import Dict, Iterator, Optional, Union, override

class HumanBrain(ComputeEnvironment):
    id: str
    static: bool = True
    
    @property
    @override
    def get_type(self) -> str:
        return "human brain"
    @property
    @override
    def get_id(self) -> str:
        return self.name

    