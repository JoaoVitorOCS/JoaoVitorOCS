"""Prepara a foto para virar ASCII: remove o fundo, aumenta o contraste local
(CLAHE) e compõe sobre branco. Saída: source-prepped.png (cinza + alfa do recorte).

Uso: python scripts/prep_photo.py source-photo.jpg
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent


def main(src: str) -> None:
    img = Image.open(src).convert("RGB")
    cut = remove(img)  # RGBA, fundo transparente
    rgba = np.array(cut)

    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Fundo vira branco puro (espaço na rampa ASCII)
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    out = gray.astype(np.float32) * alpha + 255.0 * (1.0 - alpha)
    out = np.clip(out, 0, 255).astype(np.uint8)

    # Recorta até a caixa do sujeito, com uma pequena margem
    ys, xs = np.where(alpha > 0.1)
    pad = 6
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, out.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, out.shape[1])
    out = out[y0:y1, x0:x1]
    mask = (alpha[y0:y1, x0:x1] * 255).astype(np.uint8)

    Image.fromarray(np.dstack([out, mask]), "LA").save(ROOT / "source-prepped.png")
    print(f"source-prepped.png {out.shape[1]}x{out.shape[0]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "source-photo.jpg"))
