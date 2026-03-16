"""
Legacy WebScanner interface for backward compatibility.
New code should use ScanController instead.
"""

from core.scan_controller import ScanController as WebScanner

__all__ = ['WebScanner']