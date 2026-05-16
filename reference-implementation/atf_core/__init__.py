"""
ATF Core — Reference Implementation
RFC-ATF-1: Delegation Receipts
RFC-ATF-2: Runtime Continuity Records
"""
from .receipts import create_delegation_receipt, create_runtime_continuity_record
from .verifier import verify_receipt

__all__ = [
    "create_delegation_receipt",
    "create_runtime_continuity_record",
    "verify_receipt",
]
__version__ = "1.0.0"
