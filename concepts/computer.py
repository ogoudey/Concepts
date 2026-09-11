from compute_environment import ComputeEnvironment
from typing import Dict, Iterator, Optional, Union, override

class Computer(ComputeEnvironment):
    static: bool = True

    @staticmethod
    def identify(self):
        for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
            try:
                with open(path, "r") as f:
                    return f.read().strip()
            except FileNotFoundError:
                continue
        return ""
    
    @property
    @override
    def get_type(self) -> str:
        return "computer (of unknown type)"

    @property
    @override
    def get_id(self) -> str:
        return Computer.identify()

class KinovaWithExternalCamera(Computer):
    pass
    @property
    @override
    def get_type(self) -> str:
        return "kinova with an external camera in a particular position"