# import matplotlib.pyplot as plt

# # Extract series from market_maker.history
# mids, invs, cashes = zip(*market_maker.history)
# pnls = [cash + inv * mid for mid, inv, cash in market_maker.history]
# steps = range(len(market_maker.history))

# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# ax1.plot(steps, invs, color="tab:blue")
# ax1.axhline(0, color="gray", linewidth=0.8, linestyle="--")
# ax1.set_ylabel("Inventory")
# ax1.set_title("Market Maker Inventory Over Time")

# ax2.plot(steps, pnls, color="tab:green")
# ax2.axhline(0, color="gray", linewidth=0.8, linestyle="--")
# ax2.set_ylabel("PnL")
# ax2.set_xlabel("Step")
# ax2.set_title("Market Maker PnL Over Time")

# plt.tight_layout()
# plt.show()