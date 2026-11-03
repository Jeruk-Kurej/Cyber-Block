"""Playtest: main game seperti biasa, setiap game yang selesai dicatat ke CSV (durasi, hasil, skor).

Pakai: uv run python -m tools.playtest "Nama Pemain"
Setelah window ditutup, feedback pemain diketik di terminal.
Ringkasan semua playtest: uv run python -m tools.playtest --ringkasan
"""

import argparse
import csv
import statistics
from datetime import datetime
from pathlib import Path

from config import LEVELS
from game.controller import Phase
from game.scoring import AI_WIN, HUMAN_WIN, TIMEOUT
from ui.app import App

LOG_FILE = Path("playtest/hasil_playtest.csv")
COLUMNS = ["waktu", "pemain", "level", "hasil", "durasi_detik", "giliran", "skor", "feedback"]
RESULT_NAMES = {HUMAN_WIN: "menang", AI_WIN: "kalah", TIMEOUT: "waktu habis"}


class PlaytestApp(App):
    """App biasa, ditambah pencatat durasi dan hasil setiap game."""

    def __init__(self, player):
        """App biasa plus daftar game yang sudah dicatat."""
        super().__init__()
        self.player = player
        self.rows = []
        self.tracked = None     # game yang sedang diukur
        self.duration = 0.0

    def update(self, dt):
        """Update biasa, lalu ukur durasi dan catat game yang baru selesai."""
        super().update(dt)
        if self.game is not self.tracked:
            self.tracked, self.duration = self.game, 0.0
        if self.game is None or self.duration is None:
            return
        if self.game.phase != Phase.GAME_OVER:
            self.duration += dt
            return
        self.rows.append(game_row(self.player, self.game, self.duration))
        self.duration = None    # game ini sudah dicatat


def game_row(player, game, duration):
    """Satu baris CSV dari game yang sudah selesai."""
    return {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pemain": player,
        "level": game.level["name"],
        "hasil": RESULT_NAMES[game.outcome],
        "durasi_detik": round(duration, 1),
        "giliran": game.turns_survived,
        "skor": game.score["total"],
        "feedback": "",
    }


def save(rows, path=LOG_FILE):
    """Tambahkan baris ke CSV, buat file dan header kalau belum ada."""
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    """Ringkasan untuk slide: jumlah pemain dan game, durasi, dan hasil per level."""
    durations = [float(row["durasi_detik"]) for row in rows]
    lines = [
        f"{len({row['pemain'] for row in rows})} pemain, {len(rows)} game",
        f"durasi rata-rata {statistics.mean(durations):.1f} detik, terlama {max(durations):.1f} detik",
    ]
    for level in LEVELS:
        games = [row for row in rows if row["level"] == level["name"]]
        if games:
            wins = sum(row["hasil"] == "menang" for row in games)
            lines.append(f"{level['name']}: {len(games)} game, pemain menang {wins}")
    feedback = [f"- {row['pemain']}: {row['feedback']}" for row in rows if row["feedback"]]
    return "\n".join(lines + sorted(set(feedback)))


def main():
    """Jalankan playtest untuk satu pemain, atau tampilkan ringkasan (--ringkasan)."""
    parser = argparse.ArgumentParser()
    parser.add_argument("pemain", nargs="?", default="Tanpa nama")
    parser.add_argument("--ringkasan", action="store_true", help="tampilkan ringkasan semua playtest")
    args = parser.parse_args()
    if args.ringkasan:
        with LOG_FILE.open() as f:
            print(summarize(list(csv.DictReader(f))))
        return

    app = PlaytestApp(args.pemain)
    app.run()
    if not app.rows:
        print("Tidak ada game yang selesai, tidak ada yang dicatat.")
        return
    feedback = input(f"Feedback {args.pemain} (Enter untuk lewati): ").strip()
    for row in app.rows:
        row["feedback"] = feedback
    save(app.rows)
    print(f"{len(app.rows)} game dicatat di {LOG_FILE}")


if __name__ == "__main__":
    main()
