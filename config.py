"""Semua angka yang bisa diubah-ubah di Cyber Block. Ubah di sini, tidak perlu cari di file lain."""

# ---------------------------------------------------------------- papan
BOARD_SIZE = 7          # papan 7 x 7
HUMAN_START = (0, BOARD_SIZE // 2)                # (baris, kolom) awal Human: tengah baris paling atas
AI_START = (BOARD_SIZE - 1, BOARD_SIZE // 2)     # (baris, kolom) awal AI: tengah baris paling bawah

# ---------------------------------------------------------------- AI
# depth  = berapa ply ke depan AI berpikir (depth limit)
# weight = WEIGHT di evaluation function: eval = mobility_AI - WEIGHT x mobility_Human
LEVELS = [
    {"name": "Easy", "depth": 1, "weight": 1.0},
    {"name": "Normal", "depth": 2, "weight": 2.0},
    {"name": "Hard", "depth": 3, "weight": 2.0},
]
DEFAULT_LEVEL = 1       # indeks di LEVELS: 0 = Easy, 1 = Normal, 2 = Hard

WIN_UTILITY = 1000      # nilai UTILITY untuk menang (kalah = minusnya)
PLACE_RADIUS = 2        # place candidate filtering: kandidat place hanya tile dalam jarak ini dari lawan

AI_MIN_THINK_SECONDS = 0.6   # jeda minimal giliran AI supaya langkahnya terlihat

# ---------------------------------------------------------------- chess clock
HUMAN_CLOCK_SECONDS = 60.0   # waktu total Human dalam satu game
CLOCK_URGENT_SECONDS = 10.0  # jam berkedip merah di bawah angka ini

# ---------------------------------------------------------------- skor
SCORE_WIN_BONUS = 1000
SCORE_PER_SECOND_LEFT = 10
SCORE_PER_TURN = 20

# ---------------------------------------------------------------- debug mode
DEBUG_TOP_CANDIDATES = 5     # jumlah kandidat action yang ditampilkan saat Tab ditekan

# ---------------------------------------------------------------- simulasi (tools/simulate.py)
SIM_SEED = 2025
SIM_GAMES = 20
SIM_BOT_EPSILON = 0.2
SIM_OPENING_RANDOM_PLIES = 2
