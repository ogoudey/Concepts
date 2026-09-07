from typing import Dict, Iterator, Union, override
from dataclasses import dataclass, field

@dataclass
class ComputeEnvironment:
    pass
    @property
    def get_type(self) -> str:
        return ""

@dataclass
class HumanBrain(ComputeEnvironment):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "human brain"

@dataclass
class Computer(ComputeEnvironment):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "computer (of unknown type)"

# intervening robot class?
@dataclass
class Robot(Computer):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "robot (mini-PC + robot)"

# intervening robot class?
@dataclass
class KinovaWithExternalCamera(Robot):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "kinova with an external camera in a particular position"

@dataclass
class Other:
    pass

@dataclass
class Ego(Other):
    compute_environment: ComputeEnvironment = ComputeEnvironment()


@dataclass
class Command:
    pass

@dataclass
class Cause:
    pass

@dataclass
class Action:
    value: Union[str, Other]


@dataclass
class RootEgo(Ego):
    compute_environment: Optional[ComputeEnvironment]
    command_bindings: Dict[Command, Cause]
    causal_mapping: Dict[Cause, Action] = field(default_factory=dict)

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


@dataclass
class RootDevice:
    compute_environment: ComputeEnvironment
    ego: RootEgo

