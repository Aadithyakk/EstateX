# Testing EstateX XRPL Features

## Quick Start

### 1. **Start Backend**
```bash
cd /Users/Aadithya/Downloads/Eigenrestarea
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. **Start Frontend**
```bash
# In a new terminal
cd frontend
python3 -m http.server 5173
```

### 3. **Open Browser**
```
http://localhost:5173
```

---

## What You'll See (Automatically)

### On Page Load
✅ **XRPL Proof Bar** (top-right navbar):
- Network: Testnet
- Ledger: #75,000,042 (incrementing)
- ● Live (pulsing dot)

✅ **Live Activity Feed** (auto-updates):
- Shows mock XRPL events every 6 seconds
- Check browser console: Events are logged

---

## Interactive Tests

### Test 1: Trigger Transaction Receipt
**In browser console:**
```javascript
showTransactionReceipt([
  { title: 'Trustline Created', status: 'validated', hash: '3A7F9B2E...' },
  { title: 'Payment Sent', status: 'validated', hash: '5F1D4C8A...' },
  { title: 'SGPROP Delivered', status: 'pending', hash: '7E3B6F2D...' }
])
```

**Result:** Receipt drawer slides in from right, showing transaction steps

---

### Test 2: Trigger Trustline Handshake
**In browser console:**
```javascript
showTrustlineHandshake()
```

**Result:** Modal shows handshake animation, then displays "✓ Trustline Authorized" badge

---

### Test 3: Add Activity Event
**In browser console:**
```javascript
addActivityItem('🚀 Test Event', 'This is a test event from the console')
```

**Result:** Event appears at top of activity feed with timestamp

---

### Test 4: View SGPROP/XRP Market Card
1. Go to **Properties** page
2. Click any property card
3. Scroll down to **Property Detail** page
4. Below the explainability section, you'll see:
   ```
   SGPROP/XRP Market           [● LIVE]
   Buy Price:  0.0087 XRP
   Sell Price: 0.0083 XRP
   💧 Liquidity: XRPL AMM / DEX Offers
   ```

---

## Backend Endpoints (Test in Postman/curl)

### Get Ledger Info
```bash
curl http://localhost:8000/xrpl/info
```

**Response:**
```json
{
  "ledger_index": 75000042,
  "network": "Testnet",
  "server": "wss://s.altnet.rippletest.net:51233/",
  "status": "connected"
}
```

---

### Get Transaction Status
```bash
curl http://localhost:8000/xrpl/tx/3A7F9B2E1A4C8D5F6B7E9A1C
```

**Response:**
```json
{
  "tx_hash": "3A7F9B2E1A4C8D5F6B7E9A1C",
  "status": "validated",
  "ledger_index": 75000042,
  "timestamp": "2026-01-09T10:00:00Z"
}
```

---

### Get DEX Price
```bash
curl "http://localhost:8000/xrpl/dex/price?pair=SGPROP/XRP"
```

**Response:**
```json
{
  "pair": "SGPROP/XRP",
  "bid": 0.0083,
  "ask": 0.0087,
  "spread": 0.0004,
  "source": "XRPL DEX + AMM"
}
```

---

### Get Recent Activity
```bash
curl "http://localhost:8000/xrpl/activity/recent?limit=5"
```

**Response:**
```json
[
  {
    "title": "Ledger Validated",
    "detail": "#75000042",
    "timestamp": "2026-01-09T10:00:00Z",
    "type": "ledger_closed"
  },
  {
    "title": "Trustline Authorized",
    "detail": "SGPROP token now holdable",
    "timestamp": "2026-01-09T09:59:30Z",
    "type": "trustline_created"
  }
]
```

---

### Submit Mock Transaction
```bash
curl -X POST http://localhost:8000/xrpl/tx/submit-mock \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Payment",
    "metadata": {
      "from": "rN7n7...",
      "to": "rIssuer7...",
      "amount": "1000",
      "currency": "XRP"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "tx_hash": "3A7F9B2E1A4C8D5F6B7E9A1C3D5F7A9B",
  "status": "submitted",
  "message": "Transaction submitted (mock mode)",
  "explorer_url": "https://testnet.xrpl.ws/?tx=3A7F9B2E..."
}
```

---

### Create Trustline TX
```bash
curl -X POST http://localhost:8000/xrpl/trustline/create \
  -H "Content-Type: application/json" \
  -d '{
    "account": "rN7n7otQDd6FczFgLdlqtyMVrn3Rqnf5",
    "issuer": "rIssuer123ABC456DEF789GHI012JKL",
    "currency": "SGPROP",
    "limit": "1000000000"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Trustline transaction generated",
  "transaction": {
    "method": "TrustSet",
    "account": "rN7n7...",
    "limit_amount": {
      "currency": "SGPROP",
      "issuer": "rIssuer123...",
      "value": "1000000000"
    }
  },
  "next_step": "Sign and submit this transaction to XRPL"
}
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       EstateX UI                             │
├─────────────────────────────────────────────────────────────┤
│  XRPL Proof Bar  │  Activity Feed  │  Tx Receipt Drawer     │
│  (Ledger Index)  │  (Auto-updates) │  (Slides in on trade)  │
│                                                              │
│  Property Cards  │  SGPROP/XRP    │  Trustline Handshake   │
│  (Browse)        │  Market Card   │  (On KYC approval)     │
└────────────────────┬──────────────────────────────┬──────────┘
                     │                              │
            ┌────────▼──────────────────────────────▼────────┐
            │       Frontend JavaScript (app.js)             │
            │  - startLedgerHeartbeat()                      │
            │  - showTransactionReceipt()                    │
            │  - showTrustlineHandshake()                    │
            │  - startActivityFeed()                         │
            │  - renderMarketCard()                          │
            └────────┬──────────────────────────────┬────────┘
                     │ HTTP REST API                │
         ┌───────────▼────────────┬────────────────▼────────┐
         │  Backend API Routes    │   FastAPI                │
         ├────────────────────────┼───────────────────────────┤
         │  GET  /xrpl/info       │  Ledger info            │
         │  GET  /xrpl/tx/{hash}  │  Tx status              │
         │  POST /xrpl/trustline  │  Trustline ops          │
         │  GET  /xrpl/dex/price  │  DEX quotes             │
         │  GET  /xrpl/activity   │  Activity stream        │
         │  POST /xrpl/tx/submit  │  Mock tx submission     │
         └────────┬───────────────┴───────────────┬──────────┘
                  │                               │
      ┌───────────▼────────────────────────────────▼────────┐
      │      XRPLLedgerService (backend/services/)          │
      │  - WebSocket client (mock for now)                  │
      │  - Transaction tracking                             │
      │  - Trustline creation helpers                        │
      │  - DEX price queries                                 │
      └───────────┬────────────────────────────────┬────────┘
                  │                                 │
      ┌───────────▼──────────────────────────────────▼─────┐
      │  XRPL (Real or Mock)                               │
      │  - Testnet: wss://s.altnet.rippletest.net:51233/  │
      │  - Mainnet: wss://xrpl.ws:443/                     │
      │  - Demo: Simulated ledger + mock tx hashes         │
      └──────────────────────────────────────────────────────┘
```

---

## Browser Console Debugging

### Check Ledger Index
```javascript
console.log(xrplLedgerIndex)  // Current simulated ledger
```

### View Activity Feed
```javascript
console.log(xrplActivityFeed)  // Array of events
```

### Test Market Card Rendering
```javascript
let cardHTML = renderMarketCard(870727)  // SGD price
console.log(cardHTML)
```

### Monitor Proof Bar Updates
Open **DevTools → Elements** and watch the `#proof-ledger` element update every 3.5 seconds.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **Proof Bar not updating** | Check browser console for JS errors; clear cache & reload |
| **Activity Feed not showing** | Ensure `startActivityFeed()` runs on load; check console |
| **Tx Drawer not sliding** | Check that `.tx-receipt-drawer` has `active` class; CSS must load |
| **Market Card not appearing** | Scroll to bottom of property detail; may need to wait for explanation to load |
| **Backend 404 on /xrpl/** | Ensure `xrpl_ledger_route` is registered in `backend/main.py` |

---

## Performance Tips

- **Ledger updates every 3.5s** — Safe; won't hammer the browser
- **Activity feed every 6s** — Keeps UI fresh without spam
- **Transaction receipt** — One-time animation, no continuous updates
- **No WebSocket yet** — Using polling simulation for demo (upgrade in production)

---

## Production Checklist

- [ ] Enable real `xrpl-py` WebSocket subscriptions
- [ ] Replace mock tx hashes with real XRPL tx submission
- [ ] Add wallet signing flow (Xrpl.js + Gem/Xumm)
- [ ] Query real DEX order books
- [ ] Stream real activity from ledger
- [ ] Set `XRPL_DRY_RUN=False` and configure real seeds
- [ ] Deploy to XRPL Testnet first, then Mainnet

---

**Happy testing! 🚀**
