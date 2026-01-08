# Eigenrestarea Frontend UI

## Overview

A professional, institutional-grade frontend for the XRPL Real Estate Tokenization platform. The UI reflects the serious RWA (Real-World Asset) nature of the system with clean, trustworthy design that prioritizes clarity, compliance, and user control.

## Core Principles

1. **Institutional Design** – Not crypto-bro aesthetic. Professional, trustworthy appearance suitable for real RWA investors.
2. **Transparency** – AI valuations, NAV calculations, and fees are prominently displayed and explained.
3. **Compliance-First** – KYC status, wallet verification, and trustline authorization are front-and-center.
4. **User Control** – Users maintain custody of their XRPL wallets; no private keys are stored server-side.

## Pages & Features

### 1. Dashboard
**Purpose:** Portfolio overview and quick actions
- **Portfolio Summary**: Total value, holdings count, KYC status
- **Quick Actions**: Browse properties, complete KYC, link wallet
- **Recent Activity**: Recent trades and transaction feed
- **Status Indicators**: All critical compliance states at a glance

### 2. Properties
**Purpose:** Browse and discover tokenized properties
- **Property Grid**: Responsive card-based layout with property details
- **AI Valuation Badge**: Each property displays NAV (Net Asset Value) from the XGBoost AVM
- **Filtering**: By town, flat type, price range
- **Quick Quote**: See the price breakdown (NAV + spread + fees) before trading

### 3. Property Detail
**Purpose:** In-depth property analysis before purchase
- **Property Specs**: Town, flat type, floor area, storey range, lease info
- **AVM Valuation Section**: Prominent display of AI-predicted fair market price with confidence notes
- **Property Image Placeholder**: Visual representation of property
- **Purchase CTA**: Direct path to token purchase

### 4. My Portfolio
**Purpose:** View token holdings and positions
- **Holdings Table**: Property, town, units held, current value, NAV, sell action
- **Real-Time Updates**: Values update as market prices change
- **Sell Functionality**: Divest positions directly from portfolio view

### 5. Account Settings
**Purpose:** Manage profile, KYC, and XRPL wallet
- **KYC Verification Section**:
  - Current status (Not Started → Pending → Verified)
  - Accreditation level (Individual, Accredited, Institutional)
  - Modal form for submission
- **XRPL Wallet Section**:
  - Display linked wallet address (truncated for privacy)
  - Trustline count (enabled currencies on XRPL)
  - Modal to link/update wallet
  - ⚠️ Security reminder: never share private keys
- **Transaction History Table**:
  - Date, type (buy/sell), amount, status, XRPL tx hash
  - Full audit trail of on-chain activity

## UI Components

### Modals

#### Trade Modal (Purchase Tokens)
- Property name and current NAV
- Units input (decimals supported for fractional ownership)
- **Quote Breakdown**:
  - NAV: AI-predicted price × units
  - Spread: 2% liquidity provision fee
  - Fees: 1% transaction fee
  - Total: Final price to user
- Execute Trade button → adds to portfolio, records to DB

#### KYC Modal
- Full name
- Email
- Accreditation level (required for compliance)
- Terms agreement checkbox
- Submission → status updates to "Verified"

#### Wallet Modal
- XRPL wallet address input (validation: must start with 'r')
- Custody type (self-hosted or custodian)
- Security warning
- Link → enables trading

### Responsive Design
- Desktop: Multi-column grids, full layouts
- Tablet (768px): Flexible grids, adjusted spacing
- Mobile (480px): Single-column, stacked layout, touch-friendly buttons

## Color Scheme

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary | Blue | #0052cc | Buttons, links, badges |
| Success | Green | #28a745 | AI valuations, approvals |
| Warning | Amber | #ffc107 | Pending status, alerts |
| Danger | Red | #dc3545 | Error states |
| Light | Off-white | #f8f9fa | Backgrounds, cards |
| Dark | Charcoal | #212529 | Text, headers |

## Typography

- **Font Family**: System fonts (-apple-system, Segoe UI, Roboto, etc.)
- **Sizes**:
  - 32px: Page titles
  - 24px: Card headers
  - 16px: Body text
  - 12px: Small labels
- **Monospace**: Monaco/Courier for wallet addresses and tx hashes

## API Integration

### Endpoints Used

```javascript
GET  /health              // Health check on load
POST /avm/predict         // AI valuation for property detail
POST /avm/batch_predict   // Batch valuations (future)
POST /properties          // Create listing (future)
GET  /properties          // List all properties (future)
POST /auth/kyc           // Submit KYC
POST /auth/wallet        // Link wallet
POST /trades             // Execute trade (future)
GET  /portfolio          // Load user holdings (future)
```

### Current State Management

Frontend currently uses **in-memory state** with mock data:
- `appState.portfolio` – holdings
- `appState.properties` – all available properties
- `appState.kyc` – user KYC status
- `appState.wallet` – linked XRPL address

**Next Phase**: Connect to backend endpoints for persistence.

## Running the Frontend

```bash
# From project root
cd frontend
python -m http.server 3000
# Open http://localhost:3000
```

Make sure backend is running on `http://localhost:8000` (CORS enabled for development).

## File Structure

```
frontend/
├── index.html          # Main HTML structure (11 pages, 3 modals)
├── styles.css          # Professional CSS (700+ lines, responsive)
├── app.js              # Full app logic, API integration, state management
└── README.md           # This file
```

## Key Features Implemented

✅ **Page Navigation** – Seamless switching between dashboard, properties, portfolio, account  
✅ **Property Browsing** – Grid view with filters (town, type, price)  
✅ **AI Valuation Display** – AVM predictions prominently featured  
✅ **Trading UI** – Quote breakdown, trade execution, position tracking  
✅ **KYC & Wallet Management** – Modal forms for user verification  
✅ **Portfolio View** – Holdings table with sell functionality  
✅ **Responsive Design** – Mobile, tablet, desktop layouts  
✅ **Error Handling** – Toast notifications for success/error states  
✅ **XRPL Address Validation** – Basic validation (starts with 'r')  
✅ **Security Messaging** – Warnings about private keys, public address only  

## Future Enhancements

1. **Real Backend Integration**
   - Replace mock data with API calls
   - Persist portfolio to user DB
   - Real XRPL transaction signing

2. **Advanced Filtering**
   - Yield comparisons
   - Lease remaining analysis
   - Price-to-NAV ratio

3. **Portfolio Analytics**
   - Performance charts
   - Dividend distributions
   - Tax reporting

4. **Wallet Integration**
   - XRP Ledger testnet connection
   - Trustline auto-creation
   - Balance display

5. **Governance**
   - Voting on property decisions
   - Offering terms negotiation

## Design Philosophy

This UI embodies the **serious RWA approach** outlined in the system design:

- **Separation of Concerns**: UI shows what users need to know; blockchain/AI work behind the scenes
- **Defensible Transparency**: Every price is traceable to the AVM; fees are explicit
- **Compliance-Ready**: KYC/AML hooks built into core flow, not bolt-ons
- **User Empowerment**: Users control wallets and can verify transactions on XRPL

Not a "get rich quick" DeFi app. It's institutional infrastructure for real asset ownership.

---

**Version**: 1.0 (Jan 2026)  
**Built for**: Eigenrestarea XRPL RWA Liquidity MVP
