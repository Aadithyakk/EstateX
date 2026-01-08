class XRPLClient:
    
    def __init__(self):
        self.users = {
            "alice": {"rlusd": 10000.0, "sgprop": 0.0},
            "bob": {"rlusd": 5000.0, "sgprop": 20.0}
        }
        self.sgprop_price = 100.0  # 1 SGPROP = 100 RLUSD

    def get_balance(self, user_id: str):
        return self.users.get(user_id)

    def process_trade(self, user_id: str, action: str, amount: float):
        if user_id not in self.users:
            return self._fail("User does not exist")
        if amount <= 0:
            return self._fail("Amount must be positive")
        if action == "buy":
            return self._buy_token(user_id, amount)
        if action == "sell":
            return self._sell_token(user_id, amount)

    def _buy_token(self, user_id: str, amount: float):
        user = self.users[user_id]
        cost = amount * self.sgprop_price
        if user["rlusd"] < cost:
            return self._fail("Insufficient RLUSD balance")
        user["rlusd"] -= cost
        user["sgprop"] += amount
        return self._success(f"Bought {amount} SGPROP", user)

    def _sell_token(self, user_id: str, amount: float):
        user = self.users[user_id]
        if user["sgprop"] < amount:
            return self._fail("Insufficient SGPROP balance")
        proceeds = amount * self.sgprop_price
        user["sgprop"] -= amount
        user["rlusd"] += proceeds
        return self._success(f"Sold {amount} SGPROP", user)

    def _success(self, message: str, balance: dict):
        return {"success": True, "message": message, "updated_balance": balance}

    def _fail(self, message: str):
        return {"success": False, "message": message}