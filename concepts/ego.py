from typing import Dict, Iterator, Optional, Union, override
from dataclasses import dataclass, Field
from .capability_model import Action
from pydantic import BaseModel, Field, field_serializer, field_validator
from .experience_dna import ExperienceDNA

class Ego(BaseModel):
    codebase: Optional[str]
    experience_dna: ExperienceDNA