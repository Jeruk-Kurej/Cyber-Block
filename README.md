# Cyber-Block

Prototype game isolasi 7×7 (mirip Isola) untuk AFL2 Artificial Intelligence dan rally games NPLC.
Human melawan AI yang memakai **Minimax + Alpha-Beta Pruning**. Tema pixel art cyberpunk tanpa aset eksternal.

## Persiapan (sekali saja)

Install [uv](https://docs.astral.sh/uv/). uv otomatis mengunduh Python dan pygame-ce yang dibutuhkan.

Mac / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Tutup lalu buka lagi terminal, masuk ke folder project, lalu:

```bash
uv sync
```

## Menjalankan

```bash
uv run main.py
```

Unit test:

```bash
uv run python -m unittest discover -s tests -t .
```

Simulasi AI vs bot (durasi game, waktu berpikir AI, win rate per level):

```bash
uv run python -m tools.simulate
```

Efficiency Alpha-Beta vs Minimax tanpa pruning (jumlah node dan waktu per giliran):

```bash
uv run python -m tools.simulate --compare
```

Playtest: main seperti biasa, setiap game dicatat ke `playtest/hasil_playtest.csv`, lalu lihat ringkasannya:

```bash
uv run python -m tools.playtest "Nama Pemain"
uv run python -m tools.playtest --ringkasan
```

Membuat app Mac (`.app`, Apple Silicon) untuk dibagikan:

```bash
uv run pyinstaller --windowed --noconfirm --name "Cyber-Block" --specpath build --osx-bundle-identifier id.ac.uc.cyberblock main.py
```

```bash
ditto -c -k --keepParent dist/Cyber-Block.app Cyber-Block-Mac.zip
```

## Kontrol

| Input | Fungsi |
|---|---|
| Klik kiri tile biru | Gerak (fase GERAK) |
| Klik kiri tile kosong | Pasang tembok (place): ubah tile jadi tembok dan akhiri giliran |
| Klik kanan / `Esc` | Batalkan gerak (saat fase PLACE) |
| `Tab` | Debug mode: cara AI berpikir |
| `1` `2` `3` | Pilih level di layar judul |
| `Spasi` | Mulai game |
| `R` | Kembali ke layar siap setelah game selesai |

## Aturan (problem formulation, di `rules.py`)

- **S0**: Human di `(0,3)`, AI di `(6,3)`, papan kosong, Human jalan duluan.
- **ACTIONS(s)**: satu giliran = *move* ke tetangga 8 arah yang kosong, lalu *place*: ubah satu tile kosong mana saja menjadi tembok permanen. Tile yang baru ditinggalkan boleh dipakai.
- **RESULT(s, a)**: state setelah move dan place, giliran pindah.
- **TERMINAL-TEST(s)**: pemain yang mendapat giliran tidak punya move legal, dan dia kalah.
- **UTILITY(s)** dari sisi AI: menang `+(1000 − ply)`, kalah `−(1000 − ply)`. Pengurang `ply` membuat AI memilih kemenangan tercepat dan menunda kekalahan selama mungkin. Nilainya tetap jauh di atas rentang heuristic.
- **Chess clock** Human 90 detik, hanya berjalan saat giliran Human. Waktu habis = kalah.
- **Skor**: menang `1000 + sisa_detik × 10 + giliran × 20`, kalah hanya `giliran × 20`. Semua kemenangan selalu lebih tinggi dari semua kekalahan.

## PEAS agent AI

| | |
|---|---|
| Performance | Membuat Human tidak punya move legal secepat mungkin, sambil menjaga mobility AI sendiri |
| Environment | Papan 7×7 berisi bidak Human, bidak AI, tile kosong, dan tembok |
| Actuators | Pindah bidak, ubah tile jadi tembok |
| Sensors | Seluruh state papan: posisi kedua bidak, posisi tembok, dan giliran |

## Cara kerja AI (`ai.py`)

Algoritma inti: **Minimax dengan Alpha-Beta Pruning**.
Pohon permainan Cyber-Block terlalu besar untuk dicari sampai akhir game, jadi ada tiga teknik pendukung (Tabel 1 di proposal):

- **Batas depth + fungsi evaluasi**: search berhenti di depth tertentu, lalu state dinilai dengan `mobility_AI − WEIGHT × mobility_Human`. Mobility = jumlah tile yang bisa dicapai dengan jalan paling banyak 2 langkah (`MOBILITY_STEPS` di `config.py`; 1 = hanya tile yang menempel).
- **Move ordering**: action diurutkan berdasarkan nilai evaluasi sebelum dicari, supaya pruning terjadi lebih awal.
- **Place candidate filtering**: AI hanya mempertimbangkan place di tile dalam jarak 2 dari lawan, ditambah 1 tile netral yang jauh dari kedua bidak untuk "membuang giliran" (fallback ke semua tile kosong).

Pemain di root = MAX (dalam game selalu AI), lawan = MIN. Komentar di kode menjelaskan arti α/β dan kenapa cutoff `v ≥ β` (MAX) dan `v ≤ α` (MIN) aman.
Depth tetap per level membuat keputusan AI selalu sama untuk posisi yang sama (deterministik), di laptop mana pun.
Search berjalan di background thread. Jeda minimal "berpikir" (0,6 detik) membuat giliran AI terbaca, lalu aksinya di-highlight di papan.

### Level (dipilih di layar judul)

| Level | Depth | WEIGHT | Karakter |
|---|---|---|---|
| Easy | 1 | 2 | Hanya melihat giliran sendiri |
| Normal | 2 | 2 | Memperhitungkan balasanmu, agresif mengurung |
| Hard | 3 | 2 | Melihat giliranmu dan giliran berikutnya |

Semua angka balancing ada di `config.py` (level, depth, WEIGHT, clock, skor). Semua warna, ukuran, dan font ada di `ui/theme.py`.

## Struktur

```
main.py              entry point
config.py            semua angka yang bisa diubah (papan, level, timer, skor)
rules.py             aturan game: state, move, place, ACTIONS, RESULT, TERMINAL-TEST
ai.py                evaluation function, Minimax dengan Alpha-Beta Pruning, move ordering,
                     place candidate filtering, AIPlayer (thread)
game/                controller (fase & giliran), chess_clock, scoring
ui/                  app, theme, effects, sprites, pixel_font, text,
                     board_renderer, hud, debug_overlay, title_screen,
                     game_over_overlay, input_handler
tools/               simulate (AI vs bot), playtest (catat durasi dan feedback)
tests/               unittest aturan, search, controller, clock, skor
```
