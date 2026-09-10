from typing import Dict, Iterator, Optional, Union, override
from dataclasses import dataclass, Field
from .capability_model import Action
from pydantic import BaseModel, Field, field_serializer, field_validator


class Command(BaseModel):
    model_config = {"frozen": True}
    id: str

class Cause(BaseModel):
    model_config = {"frozen": True}
    id: Optional[str] = None

class Action(BaseModel):
    model_config = {"frozen": True}
    #valuse: str
    value: Union[str, 'Other', 'Ego', 'RootEgo', 'ComputeEnvironment', 'HumanBrain', 'Computer']  # Add other types as needed


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

class ComputeEnvironment(BaseModel):
    code: Optional[Other] = None
    static: bool = False # or, leaf

    @property
    def get_type(self) -> str:
        return ""
    
    @property
    def get_id(self) -> str:
        return ""

class HumanBrain(ComputeEnvironment):
    name: Optional[str] = None # means that the wizard will fill it in.
    static: bool = True
    
    @property
    @override
    def get_type(self) -> str:
        return "human brain"
    @property
    @override
    def get_id(self) -> str:
        return self.name
class Computer(ComputeEnvironment):
    static: bool = True
    def _get_id(self):
        for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
            try:
                with open(path, "r") as f:
                    return f.read().strip()
            except FileNotFoundError:
                continue
        return None
    @property
    @override
    def get_type(self) -> str:
        return "computer (of unknown type)"
    
    @override
    def get_id(self) -> str:
        return self._get_id()

# intervening robot class?
class Robot(Computer):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "robot (often mini-PC + robot)"

class KinovaWithExternalCamera(Robot):
    
    @property
    @override
    def get_type(self) -> str:
        return "kinova with an external camera in a particular position"

class RootDevice(BaseModel):
    compute_environment: ComputeEnvironment
    next: Optional['RootDevice'] = None  # Optional reference to the next device in the chain

RootDevice.model_rebuild()
Action.model_rebuild()
RootEgo.model_rebuild(force=True)