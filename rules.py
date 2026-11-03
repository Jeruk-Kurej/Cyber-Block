"""Aturan permainan Cyber Block (problem formulation).

Isi file ini sama dengan Tabel 1 di proposal:
    Initial State  -> initial_state()
    PLAYER(s)      -> state["turn"]
    ACTIONS(s)     -> legal_actions(state)
    RESULT(s, a)   -> result(state, action)
    TERMINAL-TEST  -> is_terminal(state)

Tile ditulis sebagai (baris, kolom). (0, 0) ada di kiri atas papan.
State ditulis sebagai dictionary biasa, contoh state awal:
    {"human": (0, 3), "ai": (6, 3), "walls": set(), "turn": "human"}
Action ditulis sebagai pasangan (move, place), contoh: ((1, 3), (5, 3))
    artinya: pindah ke tile (1, 3), lalu ubah tile (5, 3) jadi tembok.
"""

from config import AI_START, BOARD_SIZE, HUMAN_START

HUMAN = "human"
AI = "ai"

# 8 arah gerak: atas-kiri, atas, atas-kanan, kiri, kanan, bawah-kiri, bawah, bawah-kanan
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# Semua tile di papan, urut dari kiri atas ke kanan bawah
ALL_TILES = [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)]


# ---------------------------------------------------------------- pemain & papan

def opponent(player):
    """Lawan dari player: human <-> ai."""
    return AI if player == HUMAN else HUMAN


def inside(row, col):
    """True jika (row, col) masih di dalam papan."""
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def neighbors(tile):
    """Tile yang bersebelahan (8 arah) dan masih di dalam papan."""
    row, col = tile
    return [(row + dr, col + dc) for dr, dc in DIRECTIONS if inside(row + dr, col + dc)]


def distance(a, b):
    """Jarak antar tile dalam jumlah langkah raja catur (8 arah)."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def format_tile(tile):
    return f"({tile[0]},{tile[1]})"


def format_action(action):
    move, place = action
    return f"gerak {format_tile(move)}, place {format_tile(place)}"


def board_text(state):
    """Papan sebagai teks: H = Human, A = AI, # = tembok, . = kosong."""
    lines = []
    for row in range(BOARD_SIZE):
        line = ""
        for col in range(BOARD_SIZE):
            tile = (row, col)
            if tile == state[HUMAN]:
                line += "H "
            elif tile == state[AI]:
                line += "A "
            elif tile in state["walls"]:
                line += "# "
            else:
                line += ". "
        lines.append(line.rstrip())
    return "\n".join(lines)


def print_board(state):
    """Cetak papan ke terminal, untuk debug."""
    print(board_text(state))


# ---------------------------------------------------------------- state

def initial_state():
    """Initial State (S0): kedua bidak di posisi awal, papan kosong, Human jalan duluan."""
    return {"human": HUMAN_START, "ai": AI_START, "walls": set(), "turn": HUMAN}


def is_empty(state, tile):
    """Tile kosong = bukan tembok dan tidak ditempati bidak."""
    return tile not in state["walls"] and tile != state["human"] and tile != state["ai"]


def copy_state(state):
    """Salinan state, supaya state lama tidak ikut berubah (penting untuk search AI)."""
    return {"human": state["human"], "ai": state["ai"], "walls": set(state["walls"]), "turn": state["turn"]}


# ---------------------------------------------------------------- move

def legal_moves(state, player):
    """Tile bersebelahan yang bisa diinjak player: bukan tembok dan bukan posisi lawan."""
    enemy = state[opponent(player)]
    return [tile for tile in neighbors(state[player]) if tile not in state["walls"] and tile != enemy]


def mobility(state, player):
    """Mobility = jumlah move legal player. Dipakai di evaluation function."""
    return len(legal_moves(state, player))


def apply_move(state, tile):
    """Bagian 1 dari action: bidak pemain yang sedang giliran pindah ke tile. Giliran belum pindah."""
    player = state["turn"]
    if tile not in legal_moves(state, player):
        raise ValueError(f"Move ilegal ke {format_tile(tile)}")
    new_state = copy_state(state)
    new_state[player] = tile
    return new_state


# ---------------------------------------------------------------- place

def legal_places(state):
    """Semua tile kosong boleh dijadikan tembok, termasuk tile yang baru ditinggalkan."""
    return [tile for tile in ALL_TILES if is_empty(state, tile)]


def apply_place(state, tile):
    """Bagian 2 dari action: tile kosong jadi tembok permanen, lalu giliran pindah ke lawan."""
    if not is_empty(state, tile):
        raise ValueError(f"Place ilegal di {format_tile(tile)}")
    new_state = copy_state(state)
    new_state["walls"].add(tile)
    new_state["turn"] = opponent(state["turn"])
    return new_state


# ---------------------------------------------------------------- ACTIONS & RESULT

def legal_actions(state):
    """ACTIONS(s): semua pasangan (move, place) yang legal untuk pemain yang sedang giliran."""
    actions = []
    for move in legal_moves(state, state["turn"]):
        after_move = apply_move(state, move)
        for place in legal_places(after_move):
            actions.append((move, place))
    return actions


def result(state, action):
    """RESULT(s, a): jalankan move lalu place."""
    move, place = action
    return apply_place(apply_move(state, move), place)


# ---------------------------------------------------------------- TERMINAL-TEST

def is_terminal(state):
    """Game selesai jika pemain yang sedang giliran tidak punya move legal."""
    return len(legal_moves(state, state["turn"])) == 0


def winner(state):
    """Pemenang = lawan dari pemain yang terkurung. None jika game belum selesai."""
    if is_terminal(state):
        return opponent(state["turn"])
    return None
