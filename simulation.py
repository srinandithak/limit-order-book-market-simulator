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