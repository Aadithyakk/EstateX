from typing import Dict


class PricingService:
    def __init__(self, fee_bps: float = 0.0025, min_spread: float = 0.005):
        self.fee_bps = fee_bps
        self.min_spread = min_spread

    def quote(self, predicted_price: float, side: str, qty: float, uncertainty: float = None) -> Dict:
        mid = predicted_price
        # simple spread: use min_spread
        spread = self.min_spread
        fee = self.fee_bps
        buy_price = mid * (1 + spread + fee)
        sell_price = mid * (1 - spread - fee)
        price = buy_price if side == "buy" else sell_price
        return {
            "mid": mid,
            "spread": spread,
            "fee_bps": fee,
            "price": price,
            "qty": qty,
        }
