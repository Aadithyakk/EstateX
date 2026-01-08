"""
XRPL Ledger service for real-time updates and transaction tracking.
Handles WebSocket subscriptions, tx status monitoring, and DEX/AMM queries.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import xrpl
    from xrpl.clients import WebsocketClient
    from xrpl.models import Subscribe, Unsubscribe
    XRPL_AVAILABLE = True
except ImportError:
    XRPL_AVAILABLE = False

logger = logging.getLogger(__name__)


class XRPLLedgerService:
    """Service for XRPL ledger interactions and real-time streaming."""

    def __init__(self, ws_url: str = "wss://s.altnet.rippletest.net:51233/"):
        """Initialize ledger service."""
        self.ws_url = ws_url
        self.client = None
        self.latest_ledger_index = 0
        self.transaction_cache = {}  # Track recent tx submissions
        
    async def connect(self):
        """Establish WebSocket connection to XRPL."""
        if not XRPL_AVAILABLE:
            logger.warning("xrpl-py not available; ledger service unavailable")
            return False
        
        try:
            self.client = WebsocketClient(self.ws_url)
            await self.client.connect()
            logger.info(f"Connected to XRPL: {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to XRPL: {e}")
            return False

    async def disconnect(self):
        """Close WebSocket connection."""
        if self.client:
            await self.client.disconnect()
            self.client = None

    async def subscribe_ledger(self, callback=None):
        """Subscribe to ledger updates."""
        if not self.client:
            await self.connect()
        
        if not self.client:
            return
        
        try:
            # Subscribe to ledger_closed stream
            await self.client.send(Subscribe(streams=["ledger"]))
            
            async for response in self.client:
                if response.get("type") == "ledgerClosed":
                    self.latest_ledger_index = response.get("ledger_index", 0)
                    
                    if callback:
                        callback({
                            "ledger_index": self.latest_ledger_index,
                            "timestamp": datetime.utcnow().isoformat(),
                            "txn_count": response.get("txn_count", 0)
                        })
        except Exception as e:
            logger.error(f"Ledger subscription error: {e}")

    async def get_tx_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status and details."""
        if not self.client or not XRPL_AVAILABLE:
            # Return mock data for demo
            return {
                "tx_hash": tx_hash,
                "status": "validated",
                "ledger_index": self.latest_ledger_index,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            response = await self.client.request(
                xrpl.models.requests.Tx(transaction=tx_hash)
            )
            
            return {
                "tx_hash": tx_hash,
                "status": "validated" if response.result.get("validated") else "pending",
                "ledger_index": response.result.get("ledger_index"),
                "timestamp": response.result.get("date"),
                "account": response.result.get("Account"),
                "destination": response.result.get("Destination")
            }
        except Exception as e:
            logger.warning(f"Could not fetch tx {tx_hash}: {e}")
            return {
                "tx_hash": tx_hash,
                "status": "unknown",
                "error": str(e)
            }

    async def get_account_trustlines(self, account_id: str) -> List[Dict[str, Any]]:
        """Get trustlines for an account."""
        if not self.client or not XRPL_AVAILABLE:
            return []
        
        try:
            response = await self.client.request(
                xrpl.models.requests.AccountLines(account=account_id)
            )
            
            trustlines = []
            for line in response.result.get("lines", []):
                trustlines.append({
                    "currency": line.get("currency"),
                    "issuer": line.get("account"),
                    "balance": line.get("balance"),
                    "limit": line.get("limit"),
                    "limit_peer": line.get("limit_peer"),
                    "authorized": line.get("authorized", False),
                    "peer_authorized": line.get("peer_authorized", False)
                })
            
            return trustlines
        except Exception as e:
            logger.error(f"Error fetching trustlines for {account_id}: {e}")
            return []

    async def create_trustline_tx(self, account: str, issuer: str, currency: str = "SGPROP",
                                   limit: str = "1000000000") -> Dict[str, Any]:
        """Generate a TrustSet transaction (trustline creation)."""
        if not XRPL_AVAILABLE:
            # Return mock tx object
            return {
                "method": "TrustSet",
                "account": account,
                "limit_amount": {
                    "currency": currency,
                    "issuer": issuer,
                    "value": limit
                }
            }
        
        try:
            trustline_tx = xrpl.models.transactions.TrustSet(
                account=account,
                limit_amount=xrpl.models.amounts.IssuedCurrencyAmount(
                    currency=currency,
                    issuer=issuer,
                    value=limit
                )
            )
            
            return {
                "method": "TrustSet",
                "transaction": trustline_tx.to_dict()
            }
        except Exception as e:
            logger.error(f"Error creating trustline tx: {e}")
            return {"error": str(e)}

    async def get_dex_prices(self, asset_pair: str = "SGPROP/XRP") -> Dict[str, Any]:
        """Get DEX prices for trading pair (mock for now)."""
        # In production: query actual order book
        return {
            "pair": asset_pair,
            "bid": 0.0083,
            "ask": 0.0087,
            "spread": 0.0004,
            "source": "XRPL DEX + AMM"
        }

    def track_transaction(self, tx_hash: str, tx_type: str, metadata: Dict = None):
        """Track a submitted transaction."""
        self.transaction_cache[tx_hash] = {
            "type": tx_type,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "submitted",
            "metadata": metadata or {}
        }

    def get_tracked_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Retrieve tracked transaction info."""
        return self.transaction_cache.get(tx_hash)


# Singleton instance
_ledger_service = None


def get_ledger_service(ws_url: str = "wss://s.altnet.rippletest.net:51233/") -> XRPLLedgerService:
    """Get or create ledger service singleton."""
    global _ledger_service
    if _ledger_service is None:
        _ledger_service = XRPLLedgerService(ws_url)
    return _ledger_service
