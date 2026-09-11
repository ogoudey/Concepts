from pydantic import BaseModel
from typing import get_origin, get_args, Union, Literal, Any, Tuple, List

from .experiencer import Experiencer
from .experience_format import ExperienceFormat
from .capability_model import CapabilityModel
from .compute_environment import ComputeEnvironment
class ExperienceStructure(BaseModel):
    compute_environments: List[ComputeEnvironment]

class SharedExperience(BaseModel):
    experiencers: List[Tuple[Experiencer, ExperienceFormat]]
    structure: ExperienceStructure

from .capability_model import RootIntegratedOutput, RootIntegratedInput
from .capability_model import ActionMapping, Input, Action
from .experience_format import ExperienceFormat
from .human import HumanBrain
from .ego import Ego, HumanEgo
from .experience_dna import ExperienceDNA

# ----- Example --------- #
experience = SharedExperience(
    experiencers=[
        (Experiencer(
            ego=HumanEgo(
                codebase="human_nature",
                experience_dna=ExperienceDNA(
                    value="human"
                ),
                name="olin2822"
            )
        ), ExperienceFormat.UNKNOWN)
    ],
    structure=ExperienceStructure(
        compute_environments=[
            HumanBrain(
                id="olin2822",
                capability_models=[
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
            
        ]
    )
)