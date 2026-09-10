# KLSR — Key Level Sweep & Rejection

A TradingView Pine Script v6 indicator that tracks 39 key market levels across 13 categories and detects two independent, same-bar price reactions at each one: sweeps and rejections. Built as a pure detection/visualization layer for a liquidity sweep-and-rejection trading strategy — it has no bias engine, no VWAP, and no order logic by design; trade construction (target selection, stop placement, order entry) stays a manual decision for the trader.

## What it tracks

39 levels across 13 categories, each independently toggleable and colorable:

- 4H open / previous high / low / mid
- Daily open / previous high / low / mid
- Monday Range high / low / mid
- Weekly, Monthly, Quarterly, and Yearly open / previous high / low / mid
- London session open/high/low (03:00–08:00 EST)
- NY session open/high/low (08:00–17:00 EST)
- Asia session open/high/low (19:00–04:00 EST)
- Fixed-time opens at 06:00, 10:00, and 14:00

## Detection logic

- **Sweep** (blue) — a fresh cross through a level, debounced via state tracking so a single sweep doesn't re-fire on every subsequent bar
- **Rejection** (orange) — a wick touches or passes the level and the candle closes back on the other side
- Reactions render as small boxes spanning the reacting candle(s)
- A clustering pass merges multiple reactions at the same level within a configurable bar window into one growing box, upgrading it to orange if any rejection occurs within the cluster

## Trading concept

The indicator supports a dual-limit-order strategy: at a rejection point, place two orders simultaneously — one targeting a higher draw on liquidity, one targeting continuation — structured so that one trade substantiates the other at 2:1 to 4:1+ reward-to-risk. The indicator's job stops at flagging the reaction; identifying the draw on liquidity and placing the orders is done manually.

## Tech

Pine Script v6, TradingView

## Status

Level coverage and detection/clustering logic are complete and in active use. A possible future port to ATAS (C#/.NET) has been explored but is deferred in favor of continued TradingView development.
