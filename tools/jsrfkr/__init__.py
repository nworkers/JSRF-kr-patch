"""Shared modules of the JSRF Korean patch tools (design 20261021-i002 §2.1).

Standard library only. Scripts under tools/ put the tools/ folder on sys.path
and import from here. Importing the package also makes the font modules
(tools/font) and analysis modules (tools/analysis) importable, since the
encoder and the patcher build on them.
"""
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(TOOLS)
# A standalone executable (Nuitka, design 20261023-i022 §8.3) unpacks the
# modules and the patch/ folder side by side into one temporary folder.
COMPILED = "__compiled__" in globals()
if COMPILED:
    ROOT = TOOLS
for _sub in ("font", "analysis"):
    _path = os.path.join(TOOLS, _sub)
    if _path not in sys.path:
        sys.path.append(_path)
