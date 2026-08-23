"""Rotated-debate protocol: ANSWERER / CRITIC / SYNTHESIZER role rotation.

Domain-agnostic by contract (R-PROTO-001): this package knows nothing about
portfolios or any other application. The core modules (model, parsing,
protocol, transcript) are dependency-free; provider access via LangChain
lives only in `engines` and is imported lazily.
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
