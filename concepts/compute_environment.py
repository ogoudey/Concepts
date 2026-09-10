from typing import Dict, Iterator, Optional, Union, override
from dataclasses import dataclass, Field
from .capability_model import Action
from pydantic import BaseModel, Field, field_serializer, field_validator

from .ego import Ego

class ComputeEnvironment(BaseModel):
    ego: Ego
    static: bool = False # or, leaf

    @property
    def get_type(self) -> str:
        return ""
    
    @property
    def get_id(self) -> str:
        return ""
