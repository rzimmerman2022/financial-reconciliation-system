"""
Compatibility shim: forward top-level imports to the real implementation in src/core.

This avoids confusion when scripts or users import description_decoder from the repo root.
"""

from src.core.description_decoder import DescriptionDecoder, decode_transaction

__all__ = [
	"DescriptionDecoder",
	"decode_transaction",
]
