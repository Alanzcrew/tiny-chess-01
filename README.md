# tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/Alanzcrew/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/Alanzcrew/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

Deterministic chess engine for make.fun `tiny-chess-01`. Entry point is `main.py` (4,068 bytes, Python 3.13, stdlib only).

Design: 0x88 board, alpha-beta search with quiescence, fixed 80,000-node budget per move (never wall-clock), transposition table with mate-score ply adjustment, MVV-LVA ordering, killer moves, history heuristic, null-move pruning (adaptive R), late-move reductions, delta pruning in quiescence, check extensions, repetition and fifty-move draw detection, formula piece-square tables with king endgame blending, bishop-pair bonus, and a rook-on-7th-rank bonus (+20).

Protocol: reads `MAKEFUN_ENV_URL`, plays each game via `POST /game` and `POST /move`, resyncs from the env's full move list. No files read, no model calls, no randomness.

Local practice trials (kit env server, 3 draws × 6 games, scored from the `outcome` field with the kit's official scorer): **13.0 points / 18 games, mean Elo 1,521** — trial-0 3.5 (Elo 1,364), trial-1 4.5 (Elo 1,545), trial-2 5.0 (Elo 1,654). That beats the submitted v4's 9.0 points / 18 (mean Elo 1,278) by 4.0 points. v4's live server grade is Elo 1,364 (3W 1D 2L on trial-0's instance), reproduced byte-for-byte locally — there is no server-vs-local gap; the earlier "1,545" figure for v4 was a misread of the `result` field (White's perspective) instead of `outcome`. Perft verified on startpos, Kiwipete and an en-passant/castling position (startpos depth 4 = 197,281 exact).

## Run it

```sh
MAKEFUN_ENV_URL=<env-url> python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
