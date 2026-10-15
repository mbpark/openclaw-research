"""
The Field Agent Protocol (TFAP) - A distributed agent communication framework
"""

__version__ = "1.0.0"
__author__ = "Wally (Field Service Agent)"
__license__ = "MIT"

# Core modules
from .beacon import FieldBeacon
from .setup_agent import setup_field_agent, load_agent_config
from .initialize import initialize_field_network
from .discovery import discover_agents, find_by_capability, refresh_beacons
from .messages import Message, MessageHandler
from .trust import TrustManager, calculate_tippss_score
from .security import encrypt_message, decrypt_message, verify_signature

__all__ = [
    "FieldBeacon",
    "setup_field_agent",
    "load_agent_config",
    "initialize_field_network",
    "discover_agents",
    "find_by_capability",
    "refresh_beacons",
    "Message",
    "MessageHandler",
    "TrustManager",
    "calculate_tippss_score",
    "encrypt_message",
    "decrypt_message",
    "verify_signature",
]
