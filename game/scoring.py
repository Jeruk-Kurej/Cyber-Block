"""Hasil akhir game dan skor yang bisa dibandingkan antar tim rally."""

from config import SCORE_PER_SECOND_LEFT, SCORE_PER_TURN, SCORE_WIN_BONUS

# Kemungkinan hasil akhir game
HUMAN_WIN = "human_win"   # AI terkurung
AI_WIN = "ai_win"         # Human terkurung
TIMEOUT = "timeout"       # waktu Human habis


def compute_score(outcome, seconds_left, turns_survived):
    """Menang: bonus menang + sisa detik x 10 + giliran x 20. Kalah: hanya giliran x 20."""
    won = outcome == HUMAN_WIN
    win_bonus = SCORE_WIN_BONUS if won else 0
    time_bonus = int(seconds_left * SCORE_PER_SECOND_LEFT) if won else 0
    turn_bonus = turns_survived * SCORE_PER_TURN
    return {
        "win_bonus": win_bonus,
        "time_bonus": time_bonus,
        "turn_bonus": turn_bonus,
        "total": win_bonus + time_bonus + turn_bonus,
    }
