from typing import Dict, Iterator
from pydantic import BaseModel
from __future__ import annotations

class RootIntegratedInputSchema(BaseModel):
    pass

class RootIntegratedOutputSchema(BaseModel):
    pass


class InputModel(BaseModel):
    integrated_schema: RootIntegratedInputSchema


class OutputModel(BaseModel):
    integrated_schema: RootIntegratedOutputSchema


class RootModel(BaseModel):
    inputs: InputModel
    outputs: OutputModel

class Input(BaseModel):
    id: str


class Action(BaseModel):
    value: Union[str, RootIntegratedInputSchema]

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

class InputSystem(BaseModel):
    inputs: RootIntegratedOutputSchema


