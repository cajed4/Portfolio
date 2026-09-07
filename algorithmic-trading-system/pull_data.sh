#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Installing dependencies (pandas, pyarrow, databento, etc.)..."
python3 -m pip install --user -r requirements.txt --quiet

set -a
source .env
set +a

echo ""
echo "Checking Databento cost estimate before pulling anything..."
python3 - <<'PY'
import databento as db
client = db.Historical()
start, end = "2026-03-02", "2026-09-02"
total = 0.0
for symbol in ["NQ", "GC"]:
    cost = client.metadata.get_cost(
        dataset="GLBX.MDP3",
        symbols=[f"{symbol}.c.0"],
        stype_in="continuous",
        schema="ohlcv-1m",
        start=start,
        end=end,
    )
    print(f"  {symbol}: ${cost:.4f}")
    total += cost
print(f"  TOTAL estimated cost: ${total:.4f}")
PY

echo ""
read -p "Proceed with the pull at the estimated cost above? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted — no data pulled, no charge."
    exit 1
fi

echo ""
echo "Pulling NQ + GC, 2026-03-02 -> 2026-09-02, ohlcv-1m..."
python3 -m data_pipeline.ingest.databento_historical \
    --symbols NQ GC \
    --start 2026-03-02 --end 2026-09-02 \
    --schema ohlcv-1m

echo ""
echo "Done. Data written to data/lake/. Let Claude know it's ready to pull back into the session."
