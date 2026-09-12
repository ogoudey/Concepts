from .compute_environment import ComputeEnvironment
from typing import Dict, Iterator, Optional, Union, override
import socket
import psutil
import ipaddress
class Computer(ComputeEnvironment):
    static: bool = True

    @staticmethod
    def identify():
        for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
            try:
                with open(path, "r") as f:
                    return f.read().strip()
            except FileNotFoundError:
                continue
        return ""
    
    @staticmethod
    def _primary_ipv4() -> str:
        """
        Returns the local IPv4 address that would be used to reach the
        outside world, without actually sending any packets.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))  # no data sent, just picks a route
            return s.getsockname()[0]
        finally:
            s.close()

    @staticmethod
    def identify_network() -> str:
        """
        Returns the CIDR notation (e.g. '10.0.4.0/24') of the subnet
        this machine's primary network interface is on.
        """
        target_ip = Computer._primary_ipv4()

        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.address == target_ip:
                    if not addr.netmask:
                        raise RuntimeError(
                            f"No netmask reported for interface {interface!r}"
                        )
                    network = ipaddress.IPv4Network(
                        f"{addr.address}/{addr.netmask}", strict=False
                    )
                    return str(network)

        raise RuntimeError(f"Could not find interface matching IP {target_ip!r}")

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