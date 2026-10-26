"""Baixa o calendário público de contribuições (sem token) e grava data/contributions.json.

Uso: python scripts/fetch_contributions.py
"""
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "JoaoVitorOCS"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"


def fetch_days() -> tuple[list[dict], int]:
    url = f"https://github.com/users/{USERNAME}/contributions"
    html = requests.get(url, headers={"User-Agent": "profile-readme"}, timeout=30)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")

    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"(\d+) contributions?", tip.get_text(strip=True))
        counts[tip.get("for")] = int(m.group(1)) if m else 0

    days = [
        {"date": td["data-date"], "level": int(td["data-level"]), "count": counts.get(td.get("id"), 0)}
        for td in soup.select("td.ContributionCalendar-day[data-date]")
    ]
    days.sort(key=lambda d: d["date"])

    h2 = soup.find(id="js-contribution-activity-description")
    m = re.search(r"([\d,]+)", h2.get_text()) if h2 else None
    total = int(m.group(1).replace(",", "")) if m else sum(d["count"] for d in days)
    return days, total


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    # sequência atual: um dia de hoje ainda vazio não quebra a sequência
    current, tail = 0, days[:]
    if tail and not tail[-1]["count"]:
        tail.pop()
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1
    return current, longest


def main() -> None:
    days, total = fetch_days()
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    data = {
        "username": USERNAME,
        "generated": date.today().isoformat(),
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "active_days": sum(1 for d in days if d["count"]),
        "monthly": dict(sorted(monthly.items())),
        "days": days,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(days)} dias, {total} contribuições, sequência {current}/{longest}")


if __name__ == "__main__":
    main()
