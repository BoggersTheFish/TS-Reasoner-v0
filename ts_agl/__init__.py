"""TS-AGL: Artificial General Language foundation.

AGL is the language-to-operation layer:
human text -> LanguageMove -> TSCall -> ResultPacket -> grounded reply.

v0 boundary:
- no external LLM
- no proof authority inside language layer
- read-only operations execute automatically
- risky operations must be staged/confirmed by a caller
"""

from ts_agl.core.types import LanguageMove, TSCall, ResultPacket, AGLTrace

__all__ = ["LanguageMove", "TSCall", "ResultPacket", "AGLTrace"]
