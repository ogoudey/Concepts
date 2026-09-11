from pydantic import BaseModel
from typing import List, Tuple
class NodeConfig(BaseModel):
    """
    Represents the network configuration for a computer.
    """
    user: str
    ip_address: str
    port: int
    password: str
    command: List[str]

class NetworkConfig(BaseModel):
    nodes: List[Tuple[str, Optional[NodeConfig]]] = []
