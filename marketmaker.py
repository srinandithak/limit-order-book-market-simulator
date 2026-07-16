import math

class MarketMaker:
    def __init__(self, book, half_spread=0.05, max_skew=0.20, scale=50,
                 fallback_price=100.0, order_qty=15):
        self.book = book
        self.half_spread = half_spread
        self.max_skew = max_skew
        self.scale = scale
        self.order_qty = order_qty  # how many shares per bid/ask each step

        self.inventory = 0
        self.cash = 0.0
        self.last_mid = fallback_price

        # Track last step's resting orders so we can reconcile fills next time
        self.bid_order_id = None
        self.ask_order_id = None
        self.bid_qty_submitted = 0
        self.ask_qty_submitted = 0

        self.history = []  # we'll fill this in once step() exists

    def step(self):
        # Reconcile fills from last step's bid
        if self.bid_order_id is not None:
            bid_order = self.book.orders[self.bid_order_id]
            filled_qty = self.bid_qty_submitted - bid_order.quantity
            if filled_qty > 0:
                self.cash -= filled_qty * bid_order.price
                self.inventory += filled_qty

        # Reconcile fills from last step's ask
        if self.ask_order_id is not None:
            ask_order = self.book.orders[self.ask_order_id]
            filled_qty = self.ask_qty_submitted - ask_order.quantity
            if filled_qty > 0:
                self.cash += filled_qty * ask_order.price
                self.inventory -= filled_qty

        last_trade = self.book.last_trade_price()
        if last_trade is not None:
            self.last_mid = last_trade
            
        # Cancel old order
        self.book.cancel_order(self.bid_order_id)
        self.book.cancel_order(self.ask_order_id)

        skew = -self.max_skew * math.tanh(self.inventory/self.scale)
        mid = self.last_mid
        bid_price = mid + skew - self.half_spread
        ask_price = mid + skew + self.half_spread

        bid_id, bid_fills = self.book.add_limit_order("buy", round(bid_price, 2), self.order_qty)
        ask_id, ask_fills = self.book.add_limit_order("sell", round(ask_price, 2), self.order_qty)

        self.bid_order_id = bid_id
        self.ask_order_id = ask_id
        self.bid_qty_submitted = self.order_qty
        self.ask_qty_submitted = self.order_qty

        self.history.append((mid, self.inventory, self.cash))

        return bid_id, ask_id    
