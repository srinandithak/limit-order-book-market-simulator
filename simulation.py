from orderbook import OrderBook
from noisetrader import NoiseTrader
from marketmaker import MarketMaker

NUM_ITERATIONS = 200
NOISE_STEPS_PER_MM_STEP = 3

book = OrderBook()
noise_trader = NoiseTrader(book, std_dev=0.09, fallback_price=100.0)
market_maker = MarketMaker(book, half_spread=0.15, max_skew=0.20, scale=50, fallback_price=100.0, order_qty=15)

for i in range(NUM_ITERATIONS):
    for _ in range(NOISE_STEPS_PER_MM_STEP):
        noise_trader.step()
    market_maker.step()

    if i % 20 == 0:
        mid = book.mid_price() or 0
        pnl = market_maker.cash + market_maker.inventory * mid
        print(f"step {i:4d} | mid={mid:.2f} | inv={market_maker.inventory:5d} | cash={market_maker.cash:10.2f} | pnl={pnl:8.2f}")

mid = book.mid_price() or 0
pnl = market_maker.cash + market_maker.inventory * mid
print(f"FINAL     | mid={mid:.2f} | inv={market_maker.inventory:5d} | cash={market_maker.cash:10.2f} | pnl={pnl:8.2f}")

import matplotlib.pyplot as plt

# Extract series from market_maker.history
mids, invs, cashes = zip(*market_maker.history)
pnls = [cash + inv * mid for mid, inv, cash in market_maker.history]
steps = range(len(market_maker.history))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax1.plot(steps, invs, color="tab:blue")
ax1.axhline(0, color="gray", linewidth=0.8, linestyle="--")
ax1.set_ylabel("Inventory")
ax1.set_title("Market Maker Inventory Over Time")

ax2.plot(steps, pnls, color="tab:green")
ax2.axhline(0, color="gray", linewidth=0.8, linestyle="--")
ax2.set_ylabel("PnL")
ax2.set_xlabel("Step")
ax2.set_title("Market Maker PnL Over Time")

plt.tight_layout()
plt.show()