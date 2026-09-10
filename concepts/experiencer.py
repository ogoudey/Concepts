from .compute_environment import ComputeEnvironment
from typing import Optional
from pydantic import BaseModel
class Experiencer(BaseModel):
    compute_environment: ComputeEnvironment
    