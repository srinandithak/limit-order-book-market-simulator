"""
Limit Order Book (LOB) core.

Design:
- Bids stored in a MAX-heap (best bid = highest price)
- Asks stored in a MIN-heap (best ask = lowest price)
- Python's heapq only implements a min-heap, so bid prices are negated
  when pushed, and negated again when read.
- Each heap entry is (price_key, timestamp, order_id) so ties at the
  same price are broken by time (price-time priority).
- Orders live in a dict (order_id -> Order) so we can cancel or check
  remaining quantity without scanning the heap. "Cancelled" or
  partially-filled orders are left in the heap and skipped lazily
  when they reach the top (cheaper than removing from the middle
  of a heap, which heapq doesn't support directly).
"""

import heapq
import itertools


class Order:
    def __init__(self, order_id, side, price, quantity, timestamp):
        self.order_id = order_id
        self.side = side          # "buy" or "sell"
        self.price = price
        self.quantity = quantity  # remaining quantity (shrinks as it fills)
        self.timestamp = timestamp
        self.active = True        # flips False when cancelled or fully filled


class OrderBook:
    def __init__(self):
        self.bids = []   # heap of (-price, timestamp, order_id)
        self.asks = []   # heap of (price, timestamp, order_id)
        self.orders = {} # order_id -> Order
        self._id_counter = itertools.count(1)
        self._clock = itertools.count(1)  # simple integer "timestamps"
        self.last_trade = None

    def _next_id(self):
        return next(self._id_counter)

    def _now(self):
        return next(self._clock)

    def add_limit_order(self, side, price, quantity):
        """
        Add a limit order. It first tries to match against the resting
        book; whatever quantity doesn't fill gets rested on the book.
        Returns (order_id, list_of_fills).
        fills is a list of (price, quantity) trades that happened.
        """
        order_id = self._next_id()
        ts = self._now()
        order = Order(order_id, side, price, quantity, ts)
        self.orders[order_id] = order

        fills = self._match(order)

        # If anything is left unfilled, rest it on the book
        if order.active and order.quantity > 0:
            if side == "buy":
                heapq.heappush(self.bids, (-price, ts, order_id))
            else:
                heapq.heappush(self.asks, (price, ts, order_id))

        return order_id, fills

    def _match(self, incoming):
        """
        Match an incoming order against the opposite side of the book
        while prices cross (buy price >= best ask, or sell price <= best bid).
        """
        fills = []
        if incoming.side == "buy":
            book, better = self.asks, lambda p: incoming.price >= p
        else:
            book, better = self.bids, lambda p: incoming.price <= -p

        while incoming.quantity > 0 and book:
            top_price_key, top_ts, top_id = book[0]
            resting = self.orders.get(top_id)

            # Skip stale entries: cancelled or already fully filled
            if resting is None or not resting.active or resting.quantity <= 0:
                heapq.heappop(book)
                continue

            if not better(top_price_key):
                break  # prices no longer cross, stop matching

            trade_qty = min(incoming.quantity, resting.quantity)
            trade_price = resting.price  # resting order sets the trade price

            incoming.quantity -= trade_qty
            resting.quantity -= trade_qty
            fills.append((trade_price, trade_qty))

            if resting.quantity <= 0:
                resting.active = False
                heapq.heappop(book)

        if incoming.quantity <= 0:
            incoming.active = False

        if fills:
            self.last_trade, _ = fills[-1] 

        return fills

    def cancel_order(self, order_id):
        order = self.orders.get(order_id)
        if order and order.active:
            order.active = False
            return True
        return False

    def best_bid(self):
        while self.bids:
            price_key, ts, oid = self.bids[0]
            order = self.orders.get(oid)
            if order and order.active and order.quantity > 0:
                return -price_key
            heapq.heappop(self.bids)
        return None

    def best_ask(self):
        while self.asks:
            price_key, ts, oid = self.asks[0]
            order = self.orders.get(oid)
            if order and order.active and order.quantity > 0:
                return price_key
            heapq.heappop(self.asks)
        return None

    def mid_price(self):
        bid, ask = self.best_bid(), self.best_ask()
        if bid is not None and ask is not None:
            return (bid + ask) / 2
        return None
    
    def last_trade_price(self):
        return self.last_trade

    def spread(self):
        bid, ask = self.best_bid(), self.best_ask()
        if bid is not None and ask is not None:
            return ask - bid
        return None


if __name__ == "__main__":
    # Quick sanity test — walk through it and confirm each result makes sense
    book = OrderBook()

    # Rest two sell orders at different prices
    book.add_limit_order("sell", 100.10, 50)
    book.add_limit_order("sell", 100.05, 30)  # better (lower) ask

    # Rest a buy order below the market
    book.add_limit_order("buy", 99.90, 40)

    print("Best bid:", book.best_bid())   # expect 99.90
    print("Best ask:", book.best_ask())   # expect 100.05 (the better sell)
    print("Mid price:", book.mid_price())
    print("Spread:", book.spread())

    # Now send an aggressive buy that crosses the spread and should fill
    order_id, fills = book.add_limit_order("buy", 100.05, 20)
    print("Fills from aggressive buy:", fills)  # expect fill at 100.05 x 20
    print("Best ask after fill:", book.best_ask())  # expect 100.05 still (30-20=10 left)