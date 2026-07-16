# Limit Order Book Market Maker Simulator

A from-scratch simulation of a limit order book with a market maker that manages inventory risk through price skewing.

## What this is

This project simulates a simplified financial market:

- **`orderbook.py`** — A limit order book implementing price-time priority matching. Bids are stored in a max-heap, asks in a min-heap, with lazy deletion for cancelled/filled orders. Tracks both best bid/ask (`mid_price()`) and the price of the most recent actual trade (`last_trade_price()`).
- **`noisetrader.py`** — Simulates random market activity. Places orders around the last known trade price with Gaussian noise, and immediately cancels anything that doesn't fill — modeling a market order rather than a resting quote.
- **`marketmaker.py`** — Quotes a bid/ask spread around the current price every step. Skews its quotes based on current inventory (using a `tanh` function) to discourage further accumulation in one direction, and to manage inventory risk over time.
- **`simulation.py`** — Runs the full simulation loop, printing inventory, cash, and PnL at intervals.

## How it works

Each simulation step:
1. The noise trader submits several random orders (buy/sell, Gaussian-distributed offset from the last trade price).
2. The market maker cancels its previous quotes, recalculates a skewed bid/ask based on current inventory, and posts new quotes.
3. Fills are reconciled: cash and inventory update based on what actually matched.

PnL is calculated as `cash + inventory * mid_price` — combining realized cash from trades with the mark-to-market value of any open inventory position.

## Key design decisions (and bugs fixed along the way)

- **Mid-price vs. last trade price:** Early versions computed "mid price" from the best resting bid/ask. This created a feedback loop, since the market maker's own quotes were usually the best price in the book — meaning its reference price was really just its own last quote. Fixed by tracking the price of the last *actual trade* separately, and using that as the reference price for both the noise trader and market maker.
- **Stale resting orders:** The noise trader originally left unfilled orders resting in the book indefinitely. Over time, these stale orders accumulated and sat at the top of book, blocking the market maker's fresh quotes from ever being reached by new incoming orders — causing the market maker to stop trading entirely after enough steps. Fixed by having the noise trader cancel any unfilled remainder of its order immediately (execute-or-cancel behavior), so only the market maker's live quotes ever rest in the book.
- **Inventory skew sizing:** With large order sizes, a single fill could push inventory most of the way up the `tanh` skew curve in one step, leaving little room for gradual course correction. Reducing per-order quantity relative to the skew's `scale` parameter allowed inventory to be corrected incrementally rather than swinging to extremes.

## Results

With tuned parameters (tight spread, moderate noise volatility, and a smaller per-order quantity relative to the skew scale), the market maker's inventory oscillates around zero rather than running away, and PnL trends upward over time — evidence that the inventory-skewing strategy is compensating the market maker for the risk it takes on.

See `inventory_pnl_chart.png` for a sample run.

## Running it

```bash
python simulation.py
```

Adjust parameters (`half_spread`, `max_skew`, `scale`, `order_qty`, noise trader `std_dev`, `NOISE_STEPS_PER_MM_STEP`) in `simulation.py` to explore different market conditions.

## Possible extensions

- Interactive mode where a user can submit their own bids/asks alongside the noise trader and market maker
- More sophisticated market maker strategies (e.g., volatility-adjusted spreads)
- Multiple market makers competing in the same book
