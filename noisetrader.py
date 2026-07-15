class NoiseTrader:
    def __init__(self, book, std_dev, fallback_price=100.0, qty_range=(1, 50)):
        self.book = book
        self.std_dev = std_dev
        self.qty_range = qty_range
        self.last_mid = fallback_price  # only used before the book ever has a price
        self.history = []
    def step(self):
        # Update last_mid only if the book currently has a real mid-price
        current_mid = self.book.mid_price()
        if current_mid is not None:
            self.last_mid = current_mid

        ref_price = self.last_mid  # always use the most recent known price
        mid_before = ref_price

        side = random.choice(["buy", "sell"])
        offset = random.gauss(0, self.std_dev)
        price = ref_price + offset if side == "buy" else ref_price - offset
        quantity = random.randint(*self.qty_range)

        order_id, fills = self.book.add_limit_order(side, round(price, 2), quantity)
        mid_after = self.book.mid_price()
        self.history.append((mid_before, mid_after))
        
        return order_id, fills