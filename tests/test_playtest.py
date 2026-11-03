"""Test pencatat playtest (tools/playtest.py)."""

import csv
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from config import LEVELS  # noqa: E402
from game.controller import GameController  # noqa: E402
from game.scoring import HUMAN_WIN  # noqa: E402
from tools.playtest import PlaytestApp, save, summarize  # noqa: E402


class PlaytestLogTest(unittest.TestCase):
    """Durasi, hasil, dan ringkasan playtest tercatat dengan benar."""

    def test_records_each_finished_game_once(self):
        app = PlaytestApp("Budi")
        app.game = GameController(LEVELS[0])
        app.update(0.5)
        app.update(0.5)
        app.game.finish(HUMAN_WIN)
        app.update(0.5)
        app.update(0.5)
        self.assertEqual(len(app.rows), 1)
        row = app.rows[0]
        self.assertEqual((row["pemain"], row["level"], row["hasil"]), ("Budi", "Easy", "menang"))
        self.assertEqual(row["durasi_detik"], 1.0)
        self.assertEqual(row["skor"], app.game.score["total"])

    def test_new_game_starts_new_duration(self):
        app = PlaytestApp("Budi")
        app.game = GameController(LEVELS[0])
        app.update(2.0)
        app.game = GameController(LEVELS[1])
        app.update(0.5)
        app.game.finish(HUMAN_WIN)
        app.update(0.1)
        self.assertEqual(app.rows[0]["durasi_detik"], 0.5)

    def test_saved_csv_gives_summary(self):
        rows = [
            {"waktu": "", "pemain": "Budi", "level": "Easy", "hasil": "menang", "durasi_detik": 40.0, "giliran": 9, "skor": 1500, "feedback": "seru"},
            {"waktu": "", "pemain": "Sinta", "level": "Hard", "hasil": "kalah", "durasi_detik": 60.0, "giliran": 7, "skor": 140, "feedback": ""},
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "hasil.csv"
            save(rows[:1], path)
            save(rows[1:], path)
            with path.open() as f:
                text = summarize(list(csv.DictReader(f)))
        self.assertIn("2 pemain, 2 game", text)
        self.assertIn("durasi rata-rata 50.0 detik", text)
        self.assertIn("Easy: 1 game, pemain menang 1", text)
        self.assertIn("- Budi: seru", text)


if __name__ == "__main__":
    unittest.main()
