# Strategy Framework — Key Levels & Volume (v3)

This is a **framework**, not a strategy: building blocks, definitions, and rules for recognizing
valid setups. Individual strategies get tuned and tested *within* this framework — the framework
is what stays constant.

**Changes from v1:** ES removed (NQ + GC only). Rejection blocks reinstated as a core confluence
factor. Volume Cumulation added alongside traded-volume levels. A Bias layer (HTF/LTF) added as
a governing filter over every setup. New sections: alerting/real-time detection system, platform
& cost plan, order flow & gamma assessment, risk/reward & prop firm fit, and a quantification &
research section that directly addresses whether this can be run as a pure algorithm, a Pine
Script–assisted discretionary tool, or a hybrid — plus your open questions.

**Changes from v2:** Options-derived levels (call wall, put wall, gamma flip) and the broader
Greek-exposure layer (gamma, delta, vanna, charm) added as a core confluence source for **both**
instruments — v2 had recommended leaving GEX out for GC specifically on a liquidity/asymmetry
argument; that argument is corrected below in §2 and §13, since gold options-derived gamma data
does exist, just from a more fragmented source than NQ's. Absorption added as a confirmation
check for testing whether a rejection is "real." One honest flag before the details: this pulls
the framework back toward more inputs and more paid data than the "keep it simple" / cost-cutting
direction from v2 — that tradeoff is yours to make and it's reflected in the updated §12 cost
table, but it's worth naming rather than quietly walking back.

## 1. Governing principle

No scalping. Every setup requires **confluence** — a level (or stacked levels) *and* volume
confirming the interaction *and* alignment with the prevailing bias — before it's tradeable.
Holding period: intraday swing (minutes to a few hours), not carried overnight by default.

Instruments: **NQ, GC.**

---

## 2. Core building blocks

### Volume-derived levels (traded volume, from the volume profile)
- **POC** — price level with the most *traded* volume in the session/lookback window.
- **Value Area High / Low (VAH / VAL)** — boundaries containing 70% of traded volume.
- **High Volume Nodes (HVN)** — local peaks in traded volume away from POC.
- **Low Volume Nodes (LVN)** — thin spots; price accelerates through these rather than reacting.

### Volume Cumulation (resting/passive volume) — new
Traded volume (above) tells you where the market *already transacted*. Volume Cumulation tells
you where size is *sitting, waiting to transact* — resting bids/offers building up at a price
over time. This is a genuinely different signal from POC/VAH/VAL and is why it's tracked
separately rather than folded into the volume profile:

- A level can have **low traded volume but heavy cumulation** (price hasn't spent time there,
  but a large resting order is parked there) — this is a level the volume profile alone would
  miss.
- A level can have **high traded volume but cumulation has been absorbed/exhausted** (the resting
  size already got run over) — this is a level the volume profile would *overweight* if you only
  looked at historical POC without checking whether the resting size is still there.
- Practically, cumulation is read from order book depth (DOM) / footprint data — where size
  repeatedly reloads at a price after being hit, versus where it thins out after being tested
  once. This is the one building block that needs order-flow-style data (DOM/footprint), not
  just OHLCV bars — see §9 on order flow for how much of this to actually use day to day.

### Price-derived key levels
Prior day/week high-low-close, session open (Globex/RTH), session VWAP.

### Rejection blocks — reinstated
The last opposing candle(s) before a strong, impulsive move (last down-close candle(s) before a
sharp rally; last up-close before a sharp drop). The zone is treated as support/resistance on a
retest, on the logic that it's the origin of aggressive, motivated order flow — similar to an
"order block" in ICT-style terminology. Reinstated as a **core** confluence factor, on equal
footing with volume-derived and price-derived levels (not a tiebreaker — a real input to the
confluence count in §4).

### Options-derived levels (Greek exposure) — new
Dealer hedging flow, inferred from the options market, produces price levels that behave like
magnets or walls independent of anything happening in the futures order book itself. Four
exposures are tracked, since these are the four that actually map to something tradeable —
"all Greeks" in practice means these, not a literal every-Greek list (see the note at the end of
this subsection for why):

- **Gamma exposure (GEX)** — the primary layer. Aggregated across the option chain
  (Γ × open interest × contract multiplier × spot), it produces:
  - **Call wall** — strike with the largest call-side gamma concentration; dealers short those
    calls hedge by selling the underlying as price rises into it, so it behaves as resistance.
  - **Put wall** — strike with the largest put-side gamma concentration; behaves as support the
    same way, in the opposite direction.
  - **Gamma flip level** — the price where net dealer gamma flips from positive (long gamma:
    dealers dampen moves, tape is calmer/mean-reverting) to negative (short gamma: dealers
    amplify moves, tape trends/accelerates). This is a **regime** signal, not a price level —
    it changes how much to trust reversal setups (A-F, H) vs. the continuation setup (G) on a given
    day, more than it marks a specific price.
- **Delta exposure (DEX)** — net directional dealer positioning across the chain. Read as a bias
  input (agrees or disagrees with the HTF/LTF bias in §3), not a level generator on its own.
- **Vanna & charm** — second-order Greeks that describe how dealer delta hedging shifts with
  changes in implied volatility (vanna) and with the passage of time toward expiration (charm).
  These don't produce fixed price levels either; they explain *timing* — e.g. a call wall that's
  been holding can stop holding as charm-driven hedging unwinds into an expiration, without price
  itself changing. Treat these as a modifier on how long a gamma-derived level should be trusted,
  not as an independent setup trigger.
- **Theta and vega exposure are excluded** — they describe option time decay and volatility
  sensitivity in aggregate, not hedging flows that move the underlying's price, so they don't
  produce anything analogous to a wall or a level. Including them would add inputs without adding
  signal, which is the opposite of what you asked for.

**Data source note (this is the corrected part from v2):** NQ's gamma exposure hedges into one
fairly unified pool (NDX/QQQ options), making it the cleaner signal. Gold's gamma is real but
split across two venues — COMEX `/GC` futures options (where the deeper institutional hedging
actually sits, but which most retail GEX tools don't fully capture) and GLD/IAU ETF options (the
accessible retail proxy most free/cheap tools — including TradingView community scripts — are
actually built from). So GC's call/put walls should be trusted somewhat less than NQ's by default,
especially away from GLD/COMEX levels that don't line up with round spot numbers — this is a
per-instrument calibration point for §10's research plan, not a reason to exclude GC (v2's
"leave GEX out of GC" call was wrong on the facts and is superseded here).

### Level interactions
- **Rejection** — price approaches, fails to close beyond, reverses.
- **Sweep (liquidity grab)** — price pierces through, fails to sustain, reverses back within a
  short window. Higher conviction than a plain rejection.
- **Acceptance / breakout** — price closes beyond and holds, typically with expanding volume.
  Continuation signal — a filter that stands down reversal setups, not a reversal setup itself.

### Absorption — new, a confirmation check on top of the interactions above
Absorption is not a fourth interaction type; it's how you test whether a rejection is a *real*
rejection or just noise. In footprint/order-flow terms: heavy, above-average aggressive volume
hits the level from one side, price fails to move through it (the level holds), and the resulting
delta is strongly one-sided with no price follow-through — the "fingerprint" of a large passive
order absorbing aggression rather than a level just quietly holding on light volume. A rejection
*with* absorption is meaningfully higher-conviction than a rejection without it; a rejection with
the opposite pattern (light volume, no real fight) is closer to noise even if the candle looks
identical on a plain price chart. This needs footprint/DOM data, same as Volume Cumulation (§2
above) — see §9 for the same automation caveat that applies there.

---

## 3. Bias layer (HTF / LTF) — new, and it governs everything above

Every setup in §5 is filtered through bias before it's considered tradeable. This is the layer
that answers "yes, price is reacting to a real level, but which direction should I actually be
willing to take."

- **HTF bias** (e.g. daily/4H structure — trend direction, which side of major value the market
  is on, higher-timeframe POC location relative to price): sets the *default* directional lean
  for the session.
- **LTF bias** (e.g. 15m/5m structure within the session): can diverge from HTF short-term, and
  is what actually times the entry within the HTF lean.
- **Rule:** don't take a setup against HTF bias unless there is a genuinely strong overlapping
  confluence stack (multiple building blocks from §2 aligned, plus a sweep rather than a plain
  rejection, plus LTF bias already turning). Counter-HTF-bias trades are the highest-scrutiny,
  lowest-frequency trade type in this framework, not a routine occurrence — this is the
  discretionary judgment call the algo/discretionary split (§8) explicitly reserves for you.
- With-HTF-bias trades get the lower confluence bar from §4; against-HTF-bias trades get a
  strictly higher one.

---

## 4. Confluence model

Minimum bar for a **with-bias** setup:
1. One volume-derived level or cumulation zone, **and**
2. One price-derived key level, rejection block, or options-derived level (call wall/put wall),
   sitting at/near the same price, **plus**
3. A level interaction (rejection or sweep) confirmed by volume behavior.

For an **against-bias** setup, require a 4th factor: either a second independent level type
stacking into the same zone (see §7 on stacked levels), or a sweep specifically (not a plain
rejection) plus visible LTF bias shift.

**Absorption upgrades conviction, it doesn't gate entry.** When footprint data is available and
absorption (§2) is present at the interaction, treat the setup as one tier higher conviction than
the confluence count alone would justify (e.g. it can substitute for the 4th factor on an
against-bias setup). Its absence isn't disqualifying — plenty of valid setups will happen without
you having footprint data open — it's a conviction multiplier, not a requirement, consistent with
how order flow is used everywhere else in this framework (§13).

**Gamma flip regime check**: before sizing conviction on any reversal setup (A-F, H), check which
side of the gamma flip level (§2) price is on. Long-gamma regime (above flip, calmer/mean-
reverting) supports reversal setups; short-gamma regime (below flip, trending/accelerating) favors
the continuation setup (G) and should raise the bar on reversal setups the same way against-bias
does. This is a day-level regime check, done once per session, not per-trade.

---

## 5. Setup taxonomy

**A. POC Rejection Reversal** — price returns to a POC aligned with a key level or rejection
block; rejects with volume fading/climaxing. Target: opposite value area edge.

**B. Value Area Edge Fade** — VAH/VAL aligned with a key level, rejected back inside value.
Target: POC, then opposite edge.

**C. Key Level Sweep Reversal** — sweep through a key level aligned with a volume-derived level
or cumulation zone, on a volume spike, reversing back through. Highest-conviction setup in the
framework — the one most likely to justify an against-HTF-bias trade if HTF bias disagrees.

**D. High Volume Node Bounce** — HVN (not session POC) aligned with a minor key level; smaller-
conviction, scaling/secondary entries only.

**E. Cumulation Defense** — new. Price repeatedly tests a level with heavy resting cumulation and
gets rejected each time without the cumulation thinning out (size keeps reloading) — read this as
the level being actively defended, distinct from a one-off rejection. Higher conviction the more
times it's tested without the resting size disappearing; invalidated the moment the cumulation
visibly gets absorbed/pulled.

**F. Rejection Block Retest** — price returns to a rejection block that also aligns with a
volume- or price-derived level; reacts in the direction of the original impulsive move.

**G. Value Area Breakout + LVN Acceleration** — continuation/filter setup, not a reversal one.
Confirms reversal setups (A/B/D/E/F/H) should stand down until the next real level.

**H. Gamma Wall Reversal** — new. Price reaches a call wall or put wall (§2) that also aligns
with a volume- or price-derived level, and rejects — the options-flow equivalent of setup A/B,
with the dealer-hedging mechanism as the reason the level exists rather than historical traded
volume. Conviction scales with the gamma-flip regime check in §4 (stronger in long-gamma regime)
and with absorption if footprint data is available. On GC, discount this setup somewhat versus NQ
per the data-source caveat in §2 — a GC wall derived only from the GLD proxy chain is a weaker
signal than an NQ wall derived from the deep, unified NDX/QQQ pool.

---

## 6. Entry, invalidation, targets

- **Entry** after confirmation (interaction complete), never anticipatory.
- **Invalidation**: close beyond the interaction's extreme.
- **Targets**: next structural level in trade direction (see §7 for handling when several levels
  are stacked).

## 7. Stacked levels / zones — answering your question directly

When multiple building blocks (POC, VAH/VAL, key level, rejection block, cumulation) fall within
a small price range rather than one exact tick, don't force a single "correct" level — **treat
the cluster as a zone**:

- **Zone construction**: cluster any building blocks within a defined tick tolerance (this
  tolerance is instrument-specific and gets fixed empirically in backtesting — NQ's tolerance
  will not be GC's) into one zone. The zone's boundaries are the nearest and farthest edge of the
  clustered levels, not a single price.
- **Zone strength = count × type diversity**: a zone with 2 overlapping *types* (e.g. POC +
  rejection block) is read as stronger than a zone with 2 levels of the *same* type (e.g. POC +
  HVN, which are both just "traded volume" saying the same thing twice). This is what should
  actually move a setup from "with-bias, standard confluence" to "even considerable
  against-bias" territory in §4.
- **Stop/target placement uses the zone edges**, not the zone's center — stop beyond the far edge
  (more room, fewer false invalidations), target the near edge of the *next* zone in the trade's
  direction (more conservative, higher hit-rate targets than reaching for a single level that
  may not be the one that actually gets touched).
- This is explicitly a hypothesis to validate, not a settled rule — §9 covers how to actually
  test whether zone strength (by this count/diversity definition) predicts reaction quality
  better than any single level type alone.

---

## 8. Algo vs. discretionary split (updated)

| Layer | Automated | Discretionary |
|---|---|---|
| Level computation (POC/VAH/VAL/HVN/LVN, key levels, rejection blocks) | Yes | — |
| Cumulation tracking | Partially — needs DOM/footprint data, harder to fully automate on retail tooling (see §9, §11) | Reading whether size is reloading or thinning |
| Options-derived levels (call/put wall, gamma flip, DEX, vanna/charm) | Yes, if fed from a GEX data source (§9, §12) — not computable from OHLCV alone | Weighing GC's weaker (GLD-proxy) signal vs. NQ's cleaner one |
| Absorption | No — requires live footprint reading, not automatable on retail tooling today | Yes, this is a manual read |
| Zone construction (§7) | Yes, once tick tolerance is fixed per instrument | — |
| HTF/LTF bias | Structure detection can be flagged algorithmically | Final bias call, especially LTF nuance |
| Interaction detection (rejection/sweep/acceptance) | Yes, rule-based | Judging cleanliness of the interaction |
| Setup classification (A-H) | Yes | Go/no-go, especially against-bias trades |
| Entry/exit execution | Can alert or semi-automate | Final trigger, trade management |

---

## 9. Quantification & feasibility — can this actually be an algorithm?

Short answer: **parts of it are cleanly quantifiable today; the part you actually care about
most — will this reaction reverse or continue — is an open statistical question, not a solved
one, and that's true for anyone running this style of strategy, not just you.**

**What's reliably quantifiable (pure algorithm territory):**
Level computation (POC/VAH/VAL/HVN/LVN from OHLCV, key levels, rejection block identification),
zone clustering, bias structure detection, and interaction classification (rejection vs. sweep vs.
acceptance) are all deterministic, rule-based, and can be computed identically by a script and by
eye. This is the entire §2, §3 (structure part), §4, §7 backbone — genuinely a solvable
engineering problem, and it's most of what the Databento/analytics code from earlier already
starts to do.

**What's not reliably quantifiable yet (the real research problem):**
Whether a given confirmed interaction resolves as reversal or continuation is a *prediction*
problem, not a detection problem. Detection (did a rejection/sweep happen) is objective;
prediction (will it hold) is probabilistic and depends on context (bias alignment, zone strength,
session, volatility regime) that we don't yet have a validated model for. This is genuinely what
your framework is trying to solve, and the honest answer is: it gets solved (or shown to not be
reliably solvable at the confidence level you'd want) through the backtesting/data-mining work in
§10 below — not through more framework design. No amount of additional rule-writing substitutes
for that empirical step.

**Pine Script–specific constraint worth knowing before betting the real-time layer on it:**
Pine Script's footprint/order-flow functions (`request.footprint()`) require TradingView
Premium/Ultimate, aren't available for all instruments/periods, and — critically — return `na`
mid-bar, so a POC computed live intraday is not reliable until the bar closes; the standard
workaround is referencing the *previous* bar's confirmed POC, not the current one, to avoid
forward-looking/repainting alerts. This means cumulation and absorption (§2), which are both
inherently live/DOM concepts, are the hardest pieces of this framework to fully automate in Pine
Script — realistically a discretionary/semi-automated read (you watching the DOM or footprint
yourself), not something the alert system in §11 can fire on with full confidence. Practically:
automate levels + zones + interaction detection + alerts (very doable); treat cumulation and
absorption confirmation as a manual discretionary check before pulling the trigger.

**Options-derived levels are a separate automation question — they're not a Pine Script data
problem, they're a data-feed problem.** Pine Script itself has no native options-chain access, so
call wall/put wall/gamma flip/DEX/vanna/charm can't be computed from inside a Pine Script the way
volume/price levels can. In practice these come from an external GEX data source and get imported
one of two ways: (a) a TradingView community/paid indicator that already publishes GEX levels for
NQ-related tickers (several exist, quality and update frequency vary — see §12), which you'd plot
alongside your own level/zone script, or (b) pulling levels from a GEX provider's own site/API
(e.g. the daily levels tools referenced in §12) and manually or semi-automatically transposing
them into your alert script's static level inputs each session. Either way, this layer updates
less frequently (many free/cheap tools refresh every 15-30 minutes, not tick-by-tick) and is
fundamentally an external-data-import problem, not something the interaction-detection logic in
§11 can derive on its own the way it derives POC/VAH/VAL from OHLCV.

**Net recommendation:** build this as a **Pine Script–assisted discretionary framework**, not a
fully autonomous algorithm — matching point 1 of the original ask (algo *and* discretionary, not
algo replacing discretion). The algorithm's job is to detect and alert on the OHLCV-derived layer
(levels, zones, interactions); your job is bias judgment, cumulation/absorption confirmation,
weighing the GEX layer (imported, not computed), and the final go/no-go — the split in §8. Note
that this now has more manual/discretionary surface area than v2's recommendation, directly as a
result of adding options Greeks and absorption — that's the real cost of this change, separate
from the dollar cost in §12.

---

## 10. Research plan — your open questions, answered as directly as they can be right now

**"Which key levels have what reaction?"**
This requires a labeled historical dataset: every time price touches each level type (POC, VAH,
VAL, HVN, key level, rejection block, zone), record what happened next (rejection/sweep/
acceptance, magnitude of the following move, whether it aligned with HTF bias). Then measure
reaction rate and average follow-through **per level type, per instrument, per session, and
conditioned on bias alignment** — not as one pooled number, since a POC reaction rate on NQ
during the NY session with HTF bias aligned is a completely different statistic from a GC HVN
reaction during Globex against bias. This is the data-mining step you flagged, and it's real
work: it means pulling historical NQ and GC data (the Databento pipeline from earlier is exactly
for this), computing every level type over history, and tagging outcomes.

**"How do we know if price reverses or continues?"**
Once the above dataset exists, this becomes a straightforward — if humbling — statistics problem:
which *features* (confluence count, zone strength/type-diversity from §7, bias alignment, sweep
vs. plain rejection, session/time, cumulation read if available) actually separate reversals from
continuations, and by how much. Given the "keep it simple" preference, the right tool here is an
interpretable model (logistic regression, or a shallow decision tree) over a handful of these
features — not a black-box ML model — so the output is a readable rule ("sweep + 2-type zone +
with-bias reacted 68% of the time historically; plain rejection + 1-level zone + against-bias
reacted 41% of the time") rather than an opaque score. That readable rule is what eventually
tightens §4's confluence thresholds from "a reasonable starting guess" to "empirically supported."
Expect this to show that reversal probability is a *spectrum* driven by confluence/bias/zone
strength, not a clean yes/no per level type — which is exactly why the framework is built around
stacking multiple factors rather than trading any single level in isolation.

**"How do we replicate this across instruments (NQ, GC, and any pair added later)?"**
The *structure* of the framework (§2-§8) is instrument-agnostic — the same building blocks and
logic apply. What is **not** portable is any numeric parameter: tick tolerance for zone
clustering, what counts as a volume "spike," typical range/volatility, and the reaction-rate
statistics from the two questions above. Each new instrument needs its own calibration pass
through the same research plan — NQ's numbers are a starting hypothesis for GC, never an
assumption.

**"Multiple levels stacked in the same area — trust one, or treat it as a zone?"**
Answered structurally in §7 (zone, not a single chosen level). The remaining open part is
*validating* that zone strength (count × type diversity) actually predicts better reactions than
picking any single level — that's folded into the same backtest/statistics work above, not a
separate task.

---

## 11. Real-time detection & alerting system

Setups won't appear on a schedule, so the plan is a Pine Script layer that watches for the
detectable parts (§9) and alerts you, rather than requiring you to watch charts all session:

1. **Level/zone script**: computes POC/VAH/VAL/HVN/LVN (session + prior-session), key levels,
   and rejection blocks; clusters them into zones per §7; plots them live.
2. **GEX overlay** (imported, not computed — see §9): call wall, put wall, and gamma flip level
   plotted as static/periodically-refreshed lines from an external GEX indicator or daily-levels
   source, feeding into the same zone clustering as everything else.
3. **Interaction script**: watches price relative to each zone and classifies
   rejection/sweep/acceptance per §2's rules, using confirmed (closed-bar) data only to avoid
   repainting.
4. **Alert conditions**: fire a TradingView alert (mobile push + optionally a webhook) when a
   zone interaction completes and meets the with-bias or against-bias confluence bar from §4.
   The alert tells you *what* fired (setup letter from §5, zone strength, bias alignment, gamma
   regime) — you then pull up the chart, do the discretionary cumulation/absorption/quality
   check, and decide.
5. Execution stays manual/semi-automated at first (see §12) — the alert gets you to the chart in
   time to catch a random-timing setup; it doesn't place the trade for you.

This requires TradingView **Premium** at minimum (Essential/Plus lack multi-condition alerts,
non-expiring alerts, and footprint/TPO tools) — see §12 for the specific plan recommendation.

---

## 12. Platform & cost plan

Current spend: ATAS + Rithmic + CME data ≈ $150+/month, before passing an eval or receiving a
payout. v2 recommended dropping that entirely down to a single TradingView Premium subscription;
adding options Greeks and absorption back in (this revision) partially reverses that:

| Piece | Recommendation | Why |
|---|---|---|
| Charting / analysis / alerts | **TradingView Premium** (~$60/mo, cheaper if paid annually) | Covers volume profile, non-expiring multi-condition alerts, and footprint/TPO — the minimum tier where §11's alert script actually works. Ultimate's extra indicator/chart slots aren't needed yet. |
| GEX levels (call/put wall, gamma flip, DEX, vanna/charm) | Start with a **free/delayed source** (e.g. a daily-levels tool covering NQ and gold, or a free/community TradingView GEX indicator) rather than paying for one immediately | These update every 15-30 minutes on the free tier, which is enough for a framework built around intraday-swing setups (not scalping) that re-checks the regime a few times a session rather than needing tick-by-tick GEX. Upgrade to a paid real-time provider (SpotGamma, GexBot, Unusual Whales-style tools generally run extra $/mo on top of TradingView) only if the free tier proves to be a real bottleneck in practice — don't pre-pay for update speed you haven't confirmed you need. |
| Execution | **Tradovate**, connected directly from TradingView (TradingView has native Tradovate broker integration — no bridge needed) | No separate platform fee beyond data/commissions; works with most prop firms (Apex, Topstep, Alpha Futures, TPT, MyFundedFutures, Tradeify all generally permit copying your own discretionary trades this way — confirm your specific firm before automating). NinjaTrader remains the fallback if a firm requires it, via a webhook bridge (CrossTrade/PickMyTrade) — extra moving part, so only add it if Tradovate isn't supported by your chosen firm. |
| Order flow / absorption (ATAS/Rithmic) | **Still drop for now, revisit sooner than v2 suggested** | This is still the ~$150+/mo piece, and absorption (§2) genuinely needs it — but it's a discretionary confirmation layer (§9), not something that blocks taking any trade. Reasonable middle ground: run without it through the eval phase using TradingView's own (Premium-tier) footprint/TPO tools where available as a lighter-weight substitute, and reintroduce full ATAS/Rithmic once there's payout income, rather than paying for it before you've banked anything. |

Net effect: still meaningfully cheaper than the current ~$150+/mo stack during the build/eval
phase (TradingView Premium + free GEX data ≈ $60/mo), but no longer the near-zero-extra-cost plan
v2 described — the GEX and absorption additions have a real cost, even using the cheapest
reasonable sourcing for each.

---

## 13. Order flow, absorption & gamma — how much to actually use

**Order flow (footprint/DOM) & absorption:** keep as a secondary, discretionary-only confirmation
— for the cumulation building block (§2, §9) and now explicitly for testing whether a rejection is
real (absorption, §2, §4) — not a required input for every trade. Your own read (helps sometimes,
feels like noise other times) matches what it structurally is here: a confirming layer for zones
that already qualify on §4's confluence bar, not a standalone signal generator. Don't require it
to take a trade; use it to add or subtract conviction when you have it open. This is unchanged
from v2 — absorption is new, but its role in the framework (confirmation, not gate) is the same
role order flow already had.

**Gamma exposure (GEX) / dealer positioning — correction from v2:** v2 recommended leaving GEX out
of the core framework specifically because it assumed GC had no comparable options-gamma overlay
to NQ's. That was inaccurate — gold does have tracked gamma exposure, sourced from COMEX `/GC`
futures options (the deeper, less publicly captured book) and GLD/IAU ETF options (the accessible
proxy most tools actually use). The real asymmetry isn't "NQ has it, GC doesn't" — it's "NQ's
signal is cleaner (one unified NDX/QQQ pool), GC's is closer to reliable at round spot/COMEX
levels that line up with the GLD proxy, and weaker elsewhere." That's a *calibration* difference
(§2, §10), not a reason to exclude GC — now included as Setup H, with the discount noted there.
Delta exposure (DEX), vanna, and charm ride along as secondary modifiers on the primary gamma
signal (§2) rather than independent triggers, which keeps the actual decision surface narrower
than "four more indicators to watch" even though four exposures are technically being tracked.

---

## 14. Risk/reward, drawdown, and prop firm fit

**R:R by setup type** (starting hypotheses — tighten with backtest data from §10, don't treat as
final): Setup C (Key Level Sweep Reversal) and Setup E (Cumulation Defense) are your
highest-conviction setups and can support a tighter stop (beyond the zone's far edge) relative to
target, plausibly 1:2–1:3. Setup B (Value Area Edge Fade) and Setup D (HVN Bounce) are lower
conviction/secondary and warrant more conservative sizing or a flatter ~1:1.5 expectation until
proven otherwise. Against-HTF-bias trades (§3) should require a *better* R:R than with-bias trades
to compensate for the added risk of fighting the higher-timeframe lean — not the same bar.

**Risk per trade:** a common, reasonable starting point for this style (intraday swing, several
setups/week rather than dozens/day) is 0.5-1% of account equity per trade — small enough that a
string of invalidations (which will happen while §10's statistics are still being validated)
doesn't threaten an eval's drawdown limit.

**Drawdown type — this matters a lot for a wide-stop swing strategy:** prop firms differ on
whether the trailing drawdown locks in *intraday* (moves with unrealized equity tick-by-tick) or
*end-of-day* (only locks at session close). Apex uses intraday trailing — a trade that runs up
unrealized profit and gives some back before you close it permanently consumes that buffer, even
though you never actually banked it. Topstep uses end-of-day trailing — intraday swings in
unrealized P&L don't touch your loss floor until the position closes, which is materially more
forgiving for a strategy that's explicitly *not* scalping and will have trades that give back some
open profit before hitting target or invalidation. **Topstep-style end-of-day trailing drawdown
is the better structural fit for this framework** than Apex-style intraday trailing, all else
equal — worth weighing against each firm's other differences (Apex: more account-size options, no
firm daily loss limit in eval, but contract-size reduction after funding and a 50%-of-payout
consistency rule; Topstep: firm daily loss limit in eval, fewer account sizes, but no consistency
rule and no post-funding contract reduction) before committing capital to an eval.

---

## 15. Explicitly out of scope

Scalping/sub-minute entries; anticipatory entries ahead of confirmation; trading setups A/B/D/E/F/H
while setup G is active against the trade direction; martingale/grid position management; theta
and vega exposure as tracked inputs (§2 — excluded as non-hedging-flow Greeks); treating gamma
exposure, order flow, cumulation, or absorption as a hard requirement to enter a with-bias trade
(all four are conviction modifiers per §4, §13, not gates) — the one exception is against-bias
trades, where §4 does require one of them (or an equivalent stacked level) as the 4th factor.

## 16. Next steps

1. Lock the alert-script build (§11) — this is now the concrete next coding task once you're
   ready to resume implementation, ahead of any backtesting.
2. Pull NQ + GC historical data (Databento pipeline already scaffolded) and run the §10 research
   plan — this is what actually answers your prediction-statistics questions, not further
   framework iteration.
3. Revisit §14's numbers once §10 produces real reaction-rate data instead of starting
   hypotheses.
