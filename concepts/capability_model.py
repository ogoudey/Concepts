from __future__ import annotations

from typing import Dict, Iterator, List, Union, Tuple, Optional
from pydantic import BaseModel
import rich
from .compute_environment import ComputeEnvironment

class RootIntegratedInput(BaseModel):
    description: str

class RootIntegratedOutput(BaseModel):
    description: str


class InputModel(BaseModel):
    integrated_schema: RootIntegratedInput


class OutputModel(BaseModel):
    integrated_schema: RootIntegratedOutput
 
class Input(BaseModel):
    description: str

class Action(BaseModel):
    description: str

class ActionMapping(BaseModel):
    mapping: List[Tuple[Input, Action]] = []

    def __getitem__(self, key: Input) -> Action:
        for k, v in self.mapping:
            if k == key:
                return v
        raise KeyError(key)

    def __setitem__(self, key: Input, value: Action) -> None:
        for i, (k, _) in enumerate(self.mapping):
            if k == key:
                self.mapping[i] = (k, value)
                return
        self.mapping.append((key, value))

    def __delitem__(self, key: Input) -> None:
        for i, (k, _) in enumerate(self.mapping):
            if k == key:
                del self.mapping[i]
                return
        raise KeyError(key)

    def __iter__(self) -> Iterator[Input]:
        return (k for k, _ in self.mapping)

    def __len__(self) -> int:
        return len(self.mapping)

    def __contains__(self, key: Input) -> bool:
        return any(k == key for k, _ in self.mapping)

    def keys(self):
        return [k for k, _ in self.mapping]

    def values(self):
        return [v for _, v in self.mapping]

    def items(self):
        return list(self.mapping)

    def get(self, key: Input, default=None):
        for k, v in self.mapping:
            if k == key:
                return v
        return default
    
class CapabilityModel(BaseModel):
    """
    Loosely models an input-output system, action-forward-ly.

    Forms (one of many in) an aspect of an experience.
    """
    inputs: List[RootIntegratedInput]
    outputs: List[RootIntegratedOutput]
    action_mappings: List[ActionMapping]

    def show(self):
        rich.print(self)

# ------------ Exampels ---------------- #
kinova_vla_capability_model = \
CapabilityModel(
    inputs=[
        RootIntegratedInput(
            description="the perceptual inputs from cameras and kinova and the governing language"
        )
    ],
    outputs=[
        RootIntegratedOutput(
            description="the actions of the kinova"
        )
    ],
    action_mappings=[
        ActionMapping(
            mapping=[
                (Input(
                    description="whatever the root outputs are"
                ),
                Action(
                    description="kinova actions"
                ))
            ]      
        )
    ]
)


groot_server_capability_model = \
CapabilityModel(
    inputs=[
        RootIntegratedInput(
            description="groot inputs"
        )
    ],
    outputs=[
        RootIntegratedOutput(
            description="groot outputs"
        )
    ],
    action_mappings=[
        ActionMapping(
            mapping=[
                (Input(
                    description="whatever the root outputs are"
                ),
                Action(
                    description="kinova actions"
                ))
            ]
        )
    ]
)