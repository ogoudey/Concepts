from typing import Dict, Iterator, Optional, Union, override
from dataclasses import dataclass, Field
from .capability_model import Action
from pydantic import BaseModel, Field, field_serializer, field_validator

class ComputeEnvironment(BaseModel):
    pass
    @property
    def get_type(self) -> str:
        return ""

class HumanBrain(ComputeEnvironment):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "human brain"

class Computer(ComputeEnvironment):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "computer (of unknown type)"

# intervening robot class?
class Robot(Computer):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "robot (mini-PC + robot)"

# intervening robot class?
class KinovaWithExternalCamera(Robot):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "kinova with an external camera in a particular position"


class Command(BaseModel):
    model_config = {"frozen": True}
    id: str

class Cause(BaseModel):
    model_config = {"frozen": True}
    id: str

class Action(BaseModel):
    model_config = {"frozen": True}
    #valuse: str
    value: Union[str, 'Other']


class Other(BaseModel):
    #causal_mapping: Dict[Cause, Action] = Field(default_factory=dict)
    command_bindings: Dict[Command, Action] = Field(default_factory=dict)
    def __getitem__(self, key: Command) -> Action:
        if key in self.command_bindings:
            return self.command_bindings[key]
        raise KeyError(f"Command '{key}' is not mapped to an Action.")


class Ego(Other):
    causal_mapping: Dict[Cause, Action] = Field(default_factory=dict)

    def __getitem__(self, key: Union[Command, Cause]) -> Action:
        # Direct lookup if key is a Cause
        if key in self.causal_mapping:
            return self.causal_mapping[key]

        # Indirect lookup: resolve Command -> Cause -> Action
        if key in self.command_bindings:
            cause = self.command_bindings[key]
            if cause in self.causal_mapping:
                return self.causal_mapping[cause]
            raise KeyError(f"Cause '{cause}' derived from Command '{key}' is not mapped to an Action.")

        raise KeyError(f"Key '{key}' is neither a recognized Command nor Cause.")


class RootEgo(Ego):
    pass

class RootDevice(BaseModel):
    compute_environment: ComputeEnvironment
    ego: RootEgo
    next: Optional['RootDevice'] = None  # Optional reference to the next device in the chain

RootDevice.model_rebuild()
Action.model_rebuild()
RootEgo.model_rebuild(force=True)