from .ego import Ego
from typing import Optional
from pydantic import BaseModel
class Experiencer(BaseModel):
    ego: Ego
    