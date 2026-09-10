from pydantic import BaseModel
from typing import get_origin, get_args, Union, Literal, Any, Tuple, List

from .experiencer import Experiencer
from .experience_format import ExperienceFormat
from .capability_model import CapabilityModel

class ExperienceStructure(BaseModel):
    models: List[CapabilityModel]

class SharedExperience(BaseModel):
    experiencers: List[Tuple[Experiencer, ExperienceFormat]]
    structure: ExperienceStructure
from .capability_model import RootIntegratedOutput, RootIntegratedInput
from .capability_model import ActionMapping, Input, Action
from .experience_format import ExperienceFormat
from .human import HumanBrain
from .ego import Ego
from .experience_dna import ExperienceDNA

# ----- Example --------- #
experience = SharedExperience(
    experiencers=[
        (Experiencer(
            compute_environment=HumanBrain(
                name="olin2822",
                ego=Ego(
                    codebase="unknown",
                    experience_dna=ExperienceDNA(
                        value="human"
                    )
                )
            )
        ), ExperienceFormat.UNKNOWN)
    ],
    structure=ExperienceStructure(
        models=[
            CapabilityModel(
                inputs=[
                    RootIntegratedInput(
                        description="everything that's an input to a human brain"
                    )
                ],
                outputs=[
                    RootIntegratedOutput(
                        description="everything that's an output of (root) human brain"
                    )
                ],
                action_mappings=[
                    ActionMapping(
                        mapping=[
                            (Input(
                                description="what I output"
                            ),
                            Action(
                                description="that actually does anything (e.g. finger taps)"
                            ))
                        ]
                    )
                ]
            )
        ]
    )
)