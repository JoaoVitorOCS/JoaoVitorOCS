"""Converte source-prepped.png em ASCII monocromático que se digita linha a linha.

Uso: python scripts/make_ascii_svg.py   (gera portrait-ascii.svg; STATIC=1 para quadro parado)
"""
from pathlib import Path

import cv2
import numpy as np

from theme import BAR_H, FG, GREEN, STATIC, frame_close, frame_open

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "portrait-ascii.svg"

RAMP = " .`:-=+*cs#%@"  # escuro (esparso) -> claro (denso): texto claro sobre fundo escuro
GAMMA = 0.8  # < 1 levanta os meios-tons do suéter e do cabelo
COLS = 110
CROP = (0.08, 0.0, 0.92, 0.82)  # x0, y0, x1, y1 em fração: fecha em rosto e mãos
CHAR_ASPECT = 0.55  # largura / altura de um glifo monoespaçado
W = 370
PAD = 14


def to_ascii(path: Path) -> list[str]:
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)  # cinza + alfa
    h, w = img.shape[:2]
    img = img[int(CROP[1] * h):int(CROP[3] * h), int(CROP[0] * w):int(CROP[2] * w)]
    h, w = img.shape[:2]
    rows = round(h / w * COLS * CHAR_ASPECT)
    small = cv2.resize(img, (COLS, rows), interpolation=cv2.INTER_AREA).astype(np.float32)
    gray, alpha = small[:, :, 0] / 255, small[:, :, -1] / 255  # cv2 lê LA como BGRA
    lo, hi = np.percentile(gray[alpha >= 0.5], (2, 98))  # estica o contraste só no sujeito
    gray = np.clip((gray - lo) / (hi - lo), 0, 1)
    idx = (gray ** GAMMA * (len(RAMP) - 1) + 0.5).astype(int)
    idx = np.maximum(idx, 1)  # dentro do recorte nada vira espaço
    idx[alpha < 0.5] = 0
    lines = ["".join(RAMP[i] for i in row).rstrip() for row in idx]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def main() -> None:
    lines = to_ascii(ROOT / "source-prepped.png")
    inner = W - 2 * PAD
    cw = inner / COLS
    lh = cw / CHAR_ASPECT
    fs = lh * 0.95
    top = BAR_H + PAD
    h = round(top + lh * len(lines) + PAD)

    defs, body = [], []
    for i, line in enumerate(lines):
        y = top + lh * (i + 1) - lh * 0.2
        row_w = cw * len(line)
        text = (f'<text x="{PAD}" y="{y:.2f}" font-size="{fs:.2f}" textLength="{row_w:.2f}" '
                f'lengthAdjust="spacingAndGlyphs" xml:space="preserve"')
        if STATIC or not line:
            body.append(f"{text}>{line}</text>")
            continue
        begin, dur = 0.3 + i * 0.045, 0.35
        ry = top + lh * i
        defs.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{ry:.2f}" width="0" height="{lh + 0.5:.2f}">'
            f'<animate attributeName="width" from="0" to="{row_w:.2f}" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        body.append(f'{text} clip-path="url(#r{i})">{line}</text>')
        # cursor em bloco que acompanha a borda da varredura
        body.append(
            f'<rect x="{PAD}" y="{ry:.2f}" width="{cw:.2f}" height="{lh:.2f}" fill="{GREEN}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + row_w:.2f}" begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + dur:.2f}s"/></rect>'
        )

    svg = frame_open(W, h, "joao@github: ~/portrait", "".join(defs))
    svg += f'<g fill="{FG}">' + "\n".join(body) + "</g>\n" + frame_close()
    OUT.write_text(svg, encoding="utf-8")
    print(f"{OUT.name}: {len(lines)} linhas, {W}x{h}")


if __name__ == "__main__":
    main()
