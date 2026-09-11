from .ego import Ego, HumanEgo
from typing import Optional, Union
from pydantic import BaseModel
class Experiencer(BaseModel):
    ego: Union[Ego, HumanEgo]
    