# TEST REPORT — make.fun tiny chess engine v6 (DRAFT, trials in progress)

**Bounty:** Build the strongest chess engine in 4 KB of Python
(https://make.fun/bounty/tiny-chess-01, $500, deadline 24 Nov 2026 17:00 UTC).
**Deliverable:** `repo/main.py` (via `makefun compress` from `repo/engine_v6.py`).
**Date:** 17 Nov 2026. **Engine:** v5 + 80.000 nodes + rook-on-7th eval term (+20).

## Koreksi besar: angka "lokal v4 = 1545" salah baca (lihat INVESTIGATION.md)

`result` di state.json memakai sudut pandang PUTIH, `outcome` memakai
sudut pandang kita. TEST_REPORT_V4/V5 salah membaca game Hitam
("1-0" dibaca menang, padahal sebagai Hitam itu kalah). Angka BENAR
trial-0 (kolom `outcome`, dikonfirmasi scorer resmi kit):

| Engine | W | D | L | Poin | Spare | Elo trial-0 |
|---|---|---|---|---|---|---|
| v3 | 4 | 1 | 1 | 4,5 | 371 | 1545 |
| v4 | 3 | 1 | 2 | 3,5 | 332 | 1364 |
| v5 | 4 | 1 | 1 | 4,5 | 329 | 1545 |

Tidak ada selisih server-vs-lokal untuk v4: server (instance trial-0 yang
sama, `instance_sha256 705d05b5…`, `state_sha256 82989cbf…` = state.json
lokal byte-identik, re-run lokal deterministik penuh) = 1364 / 3W 1D 2L /
spare 332, sama persis dengan trial lokal yang dibaca benar. v4 LEBIH
LEMAH dari v3 (−1 poin), bukan setara. Klaim "live v3 = 1451" juga salah:
submission 01a1d7f1 yang dikutip milik handle lain (coral-harbor-12);
satu-satunya entry zhe-on adalah v4 (01a1e556).

## Hasil 3 draw (trial-0/1/2, official scorer, bacaan outcome)

| Engine | trial-0 | trial-1 | trial-2 | Total /18 | Mean pts | Mean Elo |
|---|---|---|---|---|---|---|
| v4 | 3,5 (1364) | 3,0 (1279) | 2,5 (1191) | 9,0 | 3,00 | 1278 |
| v5 | 4,5 (1545) | 4,0 (1451) | 6,0 (2112*) | 14,5 | 4,83 | 1703 |
| v6 | 3,5 (1364) | 4,5 (1545) | 5,0 (1654) | 13,0 | 4,33 | 1521 |

\* trial-2 Elo 2112 adalah cap scorer; rating tak-tercap akan lebih tinggi.
v5 mengalahkan v4 5,5 poin / 18 game (+425 Elo rata-rata) — decisif.
v3 hanya diukur trial-0 (4,5).
**Dua draw pertama: v6 8,0 poin vs v5 8,5 vs v4 6,5.** v6 unggul atas
v5 di trial-1 (4,5 vs 4,0 — v6 menang lawan depth-4 Hitam yang v5
kalah) tapi tertinggal di trial-0 (3,5 vs 4,5). Maksimum total v6 =
14,0 < 14,5 v5 — v6 TIDAK bisa mengalahkan total 3-draw v5.

## Design v6 (vs v5)

- **Node budget 70.000 → 80.000.** Nol byte (angka sama panjang).
  Bench 40 posisi Stockfish: v5 18/40, 2522cp → v6a(80k) 19/40, 2393cp.
- **Rook-on-7th +20** di `evaluate()`: `if ap == 4 and (sq >> 4) ==
  (6 if w else 1): s += 20 if w else -20`. Bench v6d(80k+rook):
  19/40, 2385cp (vs 2393cp tanpa rook — setara, dalam noise).
- **DITOLAK di bench:** PVS di root (18/40, 2520cp — ordering root
  rusak oleh skor null-window), LMR reduksi-2 untuk legal>8
  (19/40, 2570cp — muncul lagi blunder 625cp G5-ply-56, over-pruning).

## Byte size

- `repo/main.py`: **4.068 byte** (limit 4.096; 28 byte spare), via kit
  `node cli/makefun.mjs compress engine_v6.py --out main.py`.
  Docstring dipangkas 3 baris → 1 baris agar muat (percobaan pertama
  4.115 byte, lewat 19 byte). Source `engine_v6.py` 15.593 byte,
  sha256 `4da2ed390568af2514ab997266ef10ed018e98ced6d45fde61a9d1a786b3f834`
  (setelah pangkas docstring); main.py sha256
  `9cbf02931efac42c556b6f206463d8a7d136f93c21816dac5c063e8e26e5233c`.

## Correctness (packed main.py)

- Perft startpos d4 = 197.281 eksak. Full suite di readable engine:
  startpos d1-d4, Kiwipete d1-d3, pos3 d1-d4 — semua eksak.
- Deterministik: packed main.py startpos 20.000 node 2x → `b1c3`,
  20.000 node, identik. Eval startpos = 0.
- Speed (lokal): 80k node fresh-state worst ~2,9–3,0 dtk (startpos
  2,99 dtk; Ruy Lopez 2,73 dtk; Najdorf 2,75 dtk). Trial-0 v6: 315
  langkah, think rata-rata 2.569 ms, maks 3.282 ms, nol > 5.000 ms.
  Server ~1,5x lebih lambat → maks ~4,9 dtk, jauh di bawah batas
  10 dtk/langkah. Trial wall jauh di bawah 1.800 dtk.

## Trial-0 v6 (resmi, kit env server)

| Game | Lawan | Kita | outcome | reason | Plies |
|---|---|---|---|---|---|
| 1 | depth-2 (855) | white | win | checkmate | 93 |
| 2 | depth-3 (1073) | black | win | checkmate | 70 |
| 3 | depth-4 (1199) | white | draw | threefold_repetition | 74 |
| 4 | nodes-100k (1392) | black | draw | threefold_repetition | 73 |
| 5 | nodes-250k (1497) | white | draw | adjudicated | 200 |
| 6 | nodes-500k (1596) | black | loss | checkmate | 169 |

**v6 trial-0: 3,5 poin, Elo 1364, spare 237 — SERI dengan v4 (3,5),
di bawah v5 (4,5).** Bench edge tidak berubah jadi poin trial-0:
v6 seri 3 game (G3, G4, G5) yang v5 menangkan (G3, G5).
Trial-1/2 menentukan apakah v6 terbukti lebih kuat dari v4/v5.

## Trial-1 v6 (resmi, kit env server)

| Game | Lawan | Kita | outcome | reason | Plies |
|---|---|---|---|---|---|
| 1 | depth-2 (855) | black | win | checkmate | 74 |
| 2 | depth-3 (1073) | white | win | checkmate | 81 |
| 3 | depth-4 (1199) | black | win | checkmate | 122 |
| 4 | nodes-100k (1392) | white | win | checkmate | 55 |
| 5 | nodes-250k (1497) | black | draw | threefold_repetition | 129 |
| 6 | nodes-500k (1596) | white | loss | checkmate | 112 |

**v6 trial-1: 4,5 poin, Elo 1545, spare 468 — TERBAIK di trial-1**
(v5 4,0; v4 3,0). 263 langkah, think rata-rata 2.449 ms, maks
3.296 ms, nol > 5.000 ms.

## Trial-2 v6 (resmi, kit env server)

| Game | Lawan | Kita | outcome | reason | Plies |
|---|---|---|---|---|---|
| 1 | depth-2 (855) | white | win | checkmate | 61 |
| 2 | depth-3 (1073) | black | win | checkmate | 78 |
| 3 | depth-4 (1199) | white | win | checkmate | 151 |
| 4 | nodes-100k (1392) | black | win | checkmate | 94 |
| 5 | nodes-250k (1497) | white | win | checkmate | 185 |
| 6 | nodes-500k (1596) | black | loss | checkmate | 121 |

**v6 trial-2: 5,0 poin, Elo 1654, spare 431** — 5 menang, 0 seri,
1 kalah (hanya nodes-500k Hitam). 322 langkah, think rata-rata
2.427 ms, maks 3.426 ms, nol > 5.000 ms. v5 menyapu trial-2 6,0
(2112, cap); v6 kalah 1 game dari v5 di draw ini.

## Verdict akhir (3-draw, 18 game per engine)

- **v6 13,0 poin (mean Elo 1521) vs v4 9,0 (1278): +4,0 poin,
  +243 Elo rata-rata — v6 TERBUKTI lebih kuat dari v4, decisif.**
  v6 menang/seri di semua perbandingan per-draw vs v4.
- **v6 13,0 vs v5 14,5 (1703): −1,5 poin, −182 Elo rata-rata.**
  v5 tetap engine terkuat menurut estimasi titik, TAPI selisih
  1,5 poin / 18 game masih dalam noise (per-trial Elo SD ~115;
  1 game flip di trial-0 atau trial-2 sudah membalikkan selisih).
  v6 unggul di trial-1, kalah tipis di trial-0 dan trial-2.
- **Rekomendasi:** v6 adalah engine submittable yang jelas lebih
  kuat dari v4 (yang live sekarang, Elo 1364). v5 (14,5) TIDAK
  boleh disubmit apa adanya (ditulis sesi lain; bundle butuh sesi
  penulis aslinya). Bila koordinator bisa mem-bundle v5 dengan
  sesi penulisnya, v5 adalah pilihan terkuat; bila tidak, v6
  adalah pengganti v4 yang aman dan terbukti.
