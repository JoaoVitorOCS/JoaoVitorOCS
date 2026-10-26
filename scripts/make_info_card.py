"""Card estilo neofetch: cargo, stack e destaques, linha a linha.

Uso: python scripts/make_info_card.py   (gera info-card.svg; STATIC=1 para quadro parado)
"""
from html import escape
from pathlib import Path

from theme import BAR_H, CYAN, FG, GREEN, MUTED, STATIC, frame_close, frame_open

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

W, H = 490, 373  # mesma altura do retrato
PAD = 20
FS = 12.5
LH = 19.5
KEY_W = 82

USER, HOST = "joao", "liveira.tech"
ROWS = [
    ("Cargo", "Arquiteto de Soluções AWS · NuageIT"),
    ("Foco", "arquiteturas de IA generativa na AWS"),
    ("Paralelo", "Head de Infraestrutura · Speake Brasil"),
    ("Antes", "Novos Negócios → Dev · NuageIT"),
    ("Certs", "AWS SAA-C03 · AWS Cloud Practitioner"),
    ("Cloud", "Lambda, ECS, EC2, ECR, Bedrock, Terraform"),
    ("Back-end", "Python, FastAPI, Node.js, NestJS"),
    ("Dados", "PostgreSQL, MongoDB"),
    ("Open src", "brain · radar · jarvis (Claude Code)"),
    ("Agora", "agente de vagas em produção na AWS"),
    ("Conteúdo", "@liveira.tech · IA na prática"),
    ("Local", "Brasília, DF"),
]
SWATCHES = ["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#f0f6fc"]


def main() -> None:
    lines = [
        f'<tspan fill="{GREEN}" font-weight="bold">{USER}</tspan><tspan fill="{FG}">@</tspan>'
        f'<tspan fill="{CYAN}" font-weight="bold">{HOST}</tspan>',
        f'<tspan fill="{MUTED}">{"-" * len(USER + "@" + HOST)}</tspan>',
    ]
    lines += [
        f'<tspan fill="{CYAN}" font-weight="bold">{escape(k)}</tspan>'
        f'<tspan x="{PAD + KEY_W}" fill="{FG}">{escape(v)}</tspan>'
        for k, v in ROWS
    ]

    style = "" if STATIC else (
        "<style>.l{opacity:0;animation:in .45s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}</style>"
    )
    body = []
    top = BAR_H + PAD + FS
    for i, line in enumerate(lines):
        delay = "" if STATIC else f' style="animation-delay:{0.6 + i * 0.12:.2f}s"'
        body.append(f'<text class="l" x="{PAD}" y="{top + i * LH:.1f}" font-size="{FS}"{delay}>{line}</text>')

    y = top + len(lines) * LH + 4
    i = len(lines)
    delay = "" if STATIC else f' style="animation-delay:{0.6 + i * 0.12:.2f}s"'
    blocks = "".join(f'<rect x="{PAD + j * 26}" y="{y:.1f}" width="22" height="14" rx="2" fill="{c}"/>'
                     for j, c in enumerate(SWATCHES))
    body.append(f'<g class="l"{delay}>{blocks}</g>')

    svg = frame_open(W, H, f"{USER}@github: ~ $ neofetch") + style + "\n".join(body) + "\n" + frame_close()
    OUT.write_text(svg, encoding="utf-8")
    print(f"{OUT.name}: {len(lines)} linhas, {W}x{H}")


if __name__ == "__main__":
    main()
