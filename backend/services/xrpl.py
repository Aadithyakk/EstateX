from typing import Optional, Dict, Any
from ..config import get_settings
import time

try:
    from xrpl.clients import JsonRpcClient
    from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission, send_reliable_submission
    from xrpl.models.transactions import TrustSet, Payment, AccountSet
    from xrpl.wallet import Wallet
    XRPL_AVAILABLE = True
except Exception:
    XRPL_AVAILABLE = False


class XRPLClient:
    def __init__(self, dry_run: bool = True):
        self.settings = get_settings()
        self.dry_run = dry_run or self.settings.XRPL_DRY_RUN
        if not self.dry_run and XRPL_AVAILABLE:
            self.client = JsonRpcClient(self.settings.XRPL_RPC_URL)
        else:
            self.client = None

    def submit_and_wait(self, tx_signed) -> Dict[str, Any]:
        if self.dry_run:
            return {"success": True, "tx_hash": "DRY_RUN_TX", "engine_result": "tesSUCCESS"}
        # send and wait
        # NOTE: simplified; real implementation should use reliable submission
        resp = send_reliable_submission(tx_signed, self.client)
        return {"success": True, "tx_hash": resp.result.get("hash"), "engine_result": resp.result.get("engine_result")}

    def create_trustline_tx(self, account: str, issuer: str, currency: str, limit: str):
        # returns unsigned tx dict (for self-custody) or submits if server-side
        if self.dry_run:
            return {"success": True, "tx": {"type": "TrustSet", "account": account, "issuer": issuer, "currency": currency, "limit": limit}}
        tx = TrustSet(account=account, limit_amount={"currency": currency, "issuer": issuer, "value": str(limit)})
        return {"success": True, "tx": tx}

    def authorize_trustline_tx(self, issuer_seed: str, account: str, currency: str):
        if self.dry_run:
            return {"success": True, "message": "authorized (dry)"}
        # Issuer must set AccountSet requireAuth and then set trust line
        issuer_wallet = Wallet(seed=issuer_seed)
        acctset = AccountSet(account=issuer_wallet.classic_address, set_flag=1)
        signed = safe_sign_and_autofill_transaction(acctset, issuer_wallet, client=self.client)
        # submit
        resp = send_reliable_submission(signed, self.client)
        return {"success": True, "tx_hash": resp.result.get("hash"), "engine_result": resp.result.get("engine_result")}

    def send_issued_currency(self, issuer_seed: str, destination: str, currency: str, amount: str):
        if self.dry_run:
            return {"success": True, "tx_hash": "DRY_SEND", "engine_result": "tesSUCCESS"}
        issuer_wallet = Wallet(seed=issuer_seed)
        payment = Payment(account=issuer_wallet.classic_address, amount={"currency": currency, "issuer": issuer_wallet.classic_address, "value": str(amount)}, destination=destination)
        signed = safe_sign_and_autofill_transaction(payment, issuer_wallet, client=self.client)
        resp = send_reliable_submission(signed, self.client)
        return {"success": True, "tx_hash": resp.result.get("hash"), "engine_result": resp.result.get("engine_result")}
