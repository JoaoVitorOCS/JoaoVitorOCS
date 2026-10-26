"""Cores e moldura de terminal compartilhadas pelos três SVGs."""
import os

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#39d353"
CYAN = "#58a6ff"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
BAR_H = 28

# STATIC=1 gera um quadro parado (prévia local / Quick Look)
STATIC = os.environ.get("STATIC") == "1"


def frame_open(w: int, h: int, title: str, extra_defs: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">
<defs>{extra_defs}</defs>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 {BAR_H} V10.5 a10 10 0 0 1 10 -10 H{w - 10.5} a10 10 0 0 1 10 10 V{BAR_H} Z" fill="{BAR}"/>
<line x1="0.5" y1="{BAR_H}" x2="{w - 0.5}" y2="{BAR_H}" stroke="{BORDER}"/>
<circle cx="16" cy="14" r="5" fill="#ff5f56"/><circle cx="32" cy="14" r="5" fill="#ffbd2e"/><circle cx="48" cy="14" r="5" fill="#27c93f"/>
<text x="{w / 2}" y="18" text-anchor="middle" font-size="11" fill="{MUTED}">{title}</text>
"""


def frame_close() -> str:
    return "</svg>\n"
