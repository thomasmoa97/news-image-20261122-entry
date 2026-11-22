# World News, 22 November 2026

[![make.fun](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/thomasmoa97/news-image-20261122-entry/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard)
[![reward](https://make.fun/badge/news-image-20261122/thomasmoa97/news-image-20261122-entry/reward.svg)](https://make.fun/bounty/news-image-20261122/leaderboard)

One image that sums up the world's news of **Sunday, 22 November 2026** — drawn
as a one-page newspaper front page with Pillow (Python 3.13, no network, fully
deterministic).

**The day's lead story:** Iran fires missiles and drones at U.S. military sites
in the Gulf — Ali Al Salem air base in Kuwait and Patriot radar sites in
Bahrain — while U.S. Central Command says its defences held, with no
casualties. Also inside: Russia's strikes on Lviv and Kryvyi Rih, Mexico's
capture of cartel boss "El Chapo Isidro", the EU–Indonesia trade deal, the
COP31 deadlock, the FBI's database-hack probe, and Hong Kong's Election
Committee vote.

## How it works

`main.py` draws the 1024×1024 infographic with Pillow and the bundled DejaVu
fonts — masthead, hero panel with a stylised Gulf map, a 2×3 grid of story
cards, and a news ticker — then writes `entry.png` to `MAKEFUN_OUTPUT_DIR`
(default `/output`).

```sh
MAKEFUN_OUTPUT_DIR=. python3 main.py
```

Two runs produce byte-identical output: no clock, no randomness, no network.

## Entry

- Competition: [news-image-20261122](https://make.fun/bounty/news-image-20261122)
- Program: `main.py` (Python 3.13 + Pillow)
- Output: `entry.png` (1024×1024 PNG)
