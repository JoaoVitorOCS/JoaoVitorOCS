"""Desenha data/contributions.json como o calendário de 53 semanas, revelado em diagonal.

Uso: python scripts/render_heatmap_svg.py   (gera contrib-heatmap.svg; STATIC=1 para quadro parado)
"""
import json
from datetime import date
from pathlib import Path

from theme import BAR_H, FG, MUTED, STATIC, frame_close, frame_open

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          nada -> mais forte (nível 5 é o topo neon)
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
WEEKDAYS = {1: "seg", 3: "qua", 5: "sex"}

W = 860
PAD = 20
LABEL_W = 33
CELL, GAP = 12, 3
STEP = CELL + GAP


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # domingo = 0
    peak = max(d["count"] for d in days) or 1

    grid_top = BAR_H + PAD + 18
    grid_left = PAD + LABEL_W
    cells, months = [], []
    last_month = None
    for i, d in enumerate(days):
        col, row = divmod(i + offset, 7)
        level = d["level"]
        if level == 4 and d["count"] >= peak * 0.75:
            level = 5
        x, y = grid_left + col * STEP, grid_top + row * STEP
        delay = "" if STATIC else f' style="animation-delay:{0.3 + col * 0.022 + row * 0.05:.2f}s"'
        cells.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'fill="{PALETTE[level]}"{delay}><title>{d["count"]} em {d["date"]}</title></rect>')
        dt = date.fromisoformat(d["date"])
        if row == 0 and dt.month != last_month and dt.day <= 7 and col < 52:
            months.append(f'<text x="{x}" y="{grid_top - 7}">{MONTHS[dt.month - 1]}</text>')
            last_month = dt.month

    labels = [f'<text x="{PAD}" y="{grid_top + r * STEP + CELL - 2}">{name}</text>' for r, name in WEEKDAYS.items()]

    foot_y = grid_top + 7 * STEP + 22
    best = data["best_day"]
    bd = date.fromisoformat(best["date"])
    stats = (f'<tspan fill="{FG}" font-weight="bold">{fmt(data["total"])}</tspan> contribuições no último ano'
             f'  ·  sequência atual <tspan fill="{FG}">{data["current_streak"]}d</tspan>'
             f'  ·  maior <tspan fill="{FG}">{data["longest_streak"]}d</tspan>'
             f'  ·  melhor dia <tspan fill="{FG}">{bd.day:02d}/{bd.month:02d} ({best["count"]})</tspan>')

    legend_x = W - PAD - 6 * STEP - 62
    legend = [f'<text x="{legend_x}" y="{foot_y}">menos</text>']
    legend += [f'<rect x="{legend_x + 38 + i * STEP}" y="{foot_y - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
               for i, c in enumerate(PALETTE)]
    legend.append(f'<text x="{legend_x + 42 + 6 * STEP}" y="{foot_y}">mais</text>')

    h = foot_y + PAD
    style = "" if STATIC else (
        "<style>.c{opacity:0;transform-box:fill-box;transform-origin:center;"
        "animation:drop .4s cubic-bezier(.2,.8,.3,1) forwards}"
        "@keyframes drop{from{opacity:0;transform:translateY(-8px) scale(.6)}to{opacity:1;transform:none}}</style>"
    )
    svg = frame_open(W, h, f"joao@github: ~ $ ./contributions.sh  ·  atualizado em {data['generated']}")
    svg += style
    svg += f'<g font-size="10" fill="{MUTED}">' + "".join(months + labels) + "</g>\n"
    svg += "<g>" + "\n".join(cells) + "</g>\n"
    svg += f'<g font-size="11" fill="{MUTED}"><text x="{PAD}" y="{foot_y}">{stats}</text>' + "".join(legend) + "</g>\n"
    svg += frame_close()
    OUT.write_text(svg, encoding="utf-8")
    print(f"{OUT.name}: {len(days)} dias, {W}x{h}")


if __name__ == "__main__":
    main()
