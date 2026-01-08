/* ============================================
   EIGENRESTAREA – Frontend Application Logic
   ============================================ */

const BASE_URL = 'http://localhost:8000';

// State Management
const appState = {
  currentUser: null,
  portfolio: [],
  properties: [],
  filteredProperties: [],
  selectedProperty: null,
  kyc: { status: 'not_started', provider_ref: null },
  wallet: { address: null, trustlines: 0 },
  trades: []
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  initializeApp();
  loadDashboardData();
});

function initializeApp() {
  setupEventListeners();
  checkHealth();
}

function setupEventListeners() {
  // Navigation
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    });
  });

  // Modal events
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
      closeModal(e.target.id);
    }
  });

  // Form submissions
  document.getElementById('kyc-form')?.addEventListener('submit', submitKYC);
  document.getElementById('wallet-form')?.addEventListener('submit', linkWallet);
}

// ============================================
// NAVIGATION & PAGE SWITCHING
// ============================================

function navigateTo(page) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  
  // Show selected page
  const pageElement = document.getElementById(`${page}-page`);
  if (pageElement) {
    pageElement.classList.add('active');
  }

  // Update nav links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.dataset.page === page);
  });

  // Load page-specific data
  if (page === 'properties') {
    loadProperties();
  } else if (page === 'portfolio') {
    loadPortfolio();
  } else if (page === 'account') {
    loadAccountData();
  }
}

// ============================================
// MODALS
// ============================================

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

// ============================================
// API CALLS
// ============================================

async function apiFetch(endpoint, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showError(error.message);
    return null;
  }
}

// ============================================
// HEALTH CHECK
// ============================================

async function checkHealth() {
  const health = await apiFetch('/health');
  if (health?.status === 'ok') {
    console.log('✓ Backend connected');
    document.getElementById('user-status').textContent = 'Connected';
  }
}

// ============================================
// DASHBOARD
// ============================================

async function loadDashboardData() {
  // Load portfolio summary
  const totalValue = appState.portfolio.reduce((sum, item) => sum + (item.value || 0), 0);
  document.getElementById('total-value').textContent = `$${totalValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
  document.getElementById('total-holdings').textContent = appState.portfolio.length;

  // Load KYC status
  updateKYCBadge();

  // Load recent trades (mock for now)
  updateRecentTrades();
}

function updateKYCBadge() {
  const badge = document.getElementById('kyc-status');
  const status = appState.kyc.status;
  
  badge.textContent = status === 'approved' ? 'Verified' : 'Pending';
  badge.classList.toggle('approved', status === 'approved');
}

function updateRecentTrades() {
  const container = document.getElementById('recent-trades');
  
  if (appState.trades.length === 0) {
    container.innerHTML = '<p class="empty-state">No trades yet</p>';
    return;
  }

  container.innerHTML = appState.trades.slice(0, 5).map(trade => `
    <div class="trade-item">
      <div class="trade-time">${new Date(trade.timestamp).toLocaleDateString()}</div>
      <div class="trade-description">${trade.property_name} - ${trade.type === 'buy' ? 'Purchased' : 'Sold'}</div>
      <div class="trade-amount">+${trade.units} units</div>
    </div>
  `).join('');
}

// ============================================
// PROPERTIES
// ============================================

async function loadProperties() {
  const container = document.getElementById('properties-grid');
  
  if (appState.filteredProperties.length === 0) {
    // Mock properties for demo
    appState.filteredProperties = generateMockProperties();
  }

  container.innerHTML = appState.filteredProperties.map(prop => `
    <div class="property-card">
      <div class="property-image">🏠</div>
      <div class="property-info">
        <div class="property-name">${prop.town}</div>
        <div class="property-town">${prop.flat_type}</div>
        <div class="property-details">
          <div>${prop.floor_area_sqm} sqm</div>
          <div>${prop.storey_range}</div>
        </div>
        <div class="property-price">$${prop.avm_value.toLocaleString()}</div>
        <div class="nav-detail">
          <span>NAV: </span>
          <strong>$${prop.avm_value.toLocaleString()}</strong>
        </div>
        <div class="property-actions">
          <button onclick="viewPropertyDetail(${prop.id})" class="btn btn-primary" style="flex:1">View</button>
          <button onclick="openTradeModal(${prop.id})" class="btn btn-secondary" style="flex:1">Trade</button>
        </div>
      </div>
    </div>
  `).join('');
}

function generateMockProperties() {
  const towns = ['ANG MO KIO', 'BEDOK', 'TAMPINES', 'CLEMENTI', 'BUKIT MERAH', 'TANJONG PAGAR'];
  const flatTypes = ['3 ROOM', '4 ROOM', '5 ROOM'];
  
  return Array.from({ length: 12 }, (_, i) => ({
    id: i + 1,
    town: towns[Math.floor(Math.random() * towns.length)],
    flat_type: flatTypes[Math.floor(Math.random() * flatTypes.length)],
    floor_area_sqm: Math.floor(Math.random() * 100) + 60,
    storey_range: `${Math.floor(Math.random() * 40)} - ${Math.floor(Math.random() * 40) + 5}`,
    avm_value: Math.floor(Math.random() * 400000) + 300000,
    lease_commence_date: '1985-01-01',
    remaining_lease: '60 years'
  }));
}

function filterProperties() {
  const town = document.getElementById('search-town').value.toUpperCase();
  const flatType = document.getElementById('filter-flat-type').value;
  const minPrice = parseInt(document.getElementById('filter-min-price').value) || 0;

  appState.filteredProperties = appState.filteredProperties.filter(prop => {
    return (!town || prop.town.includes(town)) &&
           (!flatType || prop.flat_type === flatType) &&
           (prop.avm_value >= minPrice);
  });

  loadProperties();
}

function viewPropertyDetail(propertyId) {
  const property = appState.filteredProperties.find(p => p.id === propertyId);
  if (!property) return;

  appState.selectedProperty = property;
  navigateTo('property-detail');
  loadPropertyDetail(propertyId);
}

async function loadPropertyDetail(propertyId) {
  const property = appState.filteredProperties.find(p => p.id === propertyId);
  if (!property) return;

  const container = document.getElementById('property-detail-content');
  
  // Fetch AVM prediction for this property
  const prediction = await apiFetch('/avm/predict', {
    method: 'POST',
    body: JSON.stringify({
      town: property.town,
      flat_type: property.flat_type,
      block: '123',
      street_name: 'Main Street',
      storey_range: property.storey_range,
      floor_area_sqm: property.floor_area_sqm,
      flat_model: 'Standard',
      lease_commence_date: property.lease_commence_date,
      remaining_lease: property.remaining_lease,
      txn_date: new Date().toISOString().split('T')[0]
    })
  });

  const navPrice = prediction?.predicted_price || property.avm_value;

  container.innerHTML = `
    <div class="property-detail">
      <div class="property-detail-header">
        <div>
          <div class="property-image" style="height: 250px; border-radius: 8px;">🏠</div>
        </div>
        <div>
          <h3 style="margin-bottom: 16px;">${property.town}</h3>
          <div class="property-specs">
            <div class="spec-item">
              <div class="spec-label">Flat Type</div>
              <div class="spec-value">${property.flat_type}</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">Floor Area</div>
              <div class="spec-value">${property.floor_area_sqm} sqm</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">Storey Range</div>
              <div class="spec-value">${property.storey_range}</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">Lease Commenced</div>
              <div class="spec-value">${property.lease_commence_date}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="avm-section">
        <div class="avm-label">AI-Based Valuation (XGBoost AVM)</div>
        <div class="avm-price">$${navPrice.toLocaleString('en-US', { maximumFractionDigits: 0 })}</div>
        <div class="avm-confidence">Fair market estimate based on ${property.floor_area_sqm} sqm, ${property.flat_type} in ${property.town}</div>
      </div>

      <div style="display: flex; gap: 16px;">
        <button onclick="openTradeModal(${propertyId})" class="btn btn-primary" style="flex: 1;">Purchase Tokens</button>
        <button onclick="navigateTo('properties')" class="btn btn-secondary" style="flex: 1;">Back to Listing</button>
      </div>

      <div id="explanation-section" style="display:none;">
        <h3>💡 Why This Price?</h3>
        <div id="shap-container">
          <div id="base-price">
            <strong>Model Baseline:</strong> SGD <span id="base-value">calculating...</span>
          </div>
          <div id="feature-bars" style="margin-top: 16px;">
            <p style="text-align: center; color: #666;">Analyzing features...</p>
          </div>
          <div id="confidence-band" style="margin-top: 16px;">
            <strong>Confidence Range:</strong> SGD <span id="conf-lower">...</span> – <span id="conf-upper">...</span>
            <p style="font-size: 12px; color: #666; margin-top: 8px;">Based on historical HDB transaction data and model uncertainty</p>
          </div>
        </div>
      </div>
    </div>
  `;
  
  navigateTo('property-detail');
  setTimeout(() => loadExplanation(property), 100);
}

// ============================================
// TRADING
// ============================================

function openTradeModal(propertyId) {
  const property = appState.filteredProperties.find(p => p.id === propertyId);
  if (!property) return;

  appState.selectedProperty = property;
  
  document.getElementById('trade-property-name').textContent = `${property.town} ${property.flat_type}`;
  document.getElementById('trade-nav').textContent = `$${property.avm_value.toLocaleString()}`;
  document.getElementById('trade-units').value = '';
  document.getElementById('trade-units').addEventListener('input', updateQuote);

  openModal('trade-modal');
}

function updateQuote() {
  const units = parseFloat(document.getElementById('trade-units').value) || 0;
  const navPrice = appState.selectedProperty?.avm_value || 0;

  const unitPrice = navPrice / 1000; // Assume 1000 units per property
  const nav = units * unitPrice;
  const spread = nav * 0.02; // 2% spread
  const fees = nav * 0.01; // 1% fees
  const total = nav + spread + fees;

  document.getElementById('quote-nav').textContent = `$${nav.toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  document.getElementById('quote-spread').textContent = `$${spread.toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  document.getElementById('quote-fees').textContent = `$${fees.toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  document.getElementById('quote-total').textContent = `$${total.toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
}

async function executeTrade() {
  const units = parseFloat(document.getElementById('trade-units').value);
  
  if (!units || units <= 0) {
    showError('Please enter a valid number of units');
    return;
  }

  if (!appState.kyc.status === 'approved') {
    showError('Please complete KYC verification first');
    openModal('kyc-modal');
    return;
  }

  if (!appState.wallet.address) {
    showError('Please link your XRPL wallet');
    openModal('wallet-modal');
    return;
  }

  console.log('Executing trade:', { units, property: appState.selectedProperty });
  
  // Add to portfolio
  appState.portfolio.push({
    property_id: appState.selectedProperty.id,
    property_name: `${appState.selectedProperty.town} ${appState.selectedProperty.flat_type}`,
    units: units,
    value: units * (appState.selectedProperty.avm_value / 1000),
    purchased_at: new Date().toISOString()
  });

  appState.trades.push({
    property_name: `${appState.selectedProperty.town} ${appState.selectedProperty.flat_type}`,
    type: 'buy',
    units: units,
    timestamp: new Date().toISOString()
  });

  showSuccess(`Successfully purchased ${units} units!`);
  closeModal('trade-modal');
  loadDashboardData();
}

// ============================================
// PORTFOLIO
// ============================================

async function loadPortfolio() {
  const tbody = document.getElementById('holdings-body');

  if (appState.portfolio.length === 0) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="6" class="empty-state">No holdings yet. Start by purchasing a property.</td></tr>';
    return;
  }

  tbody.innerHTML = appState.portfolio.map((holding, i) => `
    <tr>
      <td>${holding.property_name}</td>
      <td>${holding.property_name.split(' ')[0]}</td>
      <td>${holding.units.toFixed(3)}</td>
      <td>$${holding.value.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
      <td>$${(holding.value / holding.units).toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
      <td>
        <button onclick="sellHolding(${i})" class="btn btn-small" style="color: #dc3545;">Sell</button>
      </td>
    </tr>
  `).join('');
}

function sellHolding(index) {
  appState.portfolio.splice(index, 1);
  loadPortfolio();
  loadDashboardData();
  showSuccess('Holding sold successfully');
}

// ============================================
// ACCOUNT
// ============================================

async function loadAccountData() {
  // KYC Status
  const kycBadge = document.getElementById('kyc-status-detail');
  const kycMessage = document.getElementById('kyc-message');
  
  if (appState.kyc.status === 'approved') {
    kycBadge.textContent = 'Verified';
    kycBadge.classList.add('approved');
    kycMessage.textContent = 'Your identity has been verified.';
  } else {
    kycBadge.textContent = 'Pending';
    kycMessage.textContent = 'Complete KYC verification to start trading.';
  }

  // Wallet Status
  const walletAddress = document.getElementById('wallet-address');
  if (appState.wallet.address) {
    walletAddress.textContent = appState.wallet.address.substring(0, 10) + '...' + appState.wallet.address.substring(appState.wallet.address.length - 6);
    document.getElementById('trustline-count').textContent = appState.wallet.trustlines;
  }

  // Transaction History
  const txBody = document.getElementById('tx-body');
  if (appState.trades.length === 0) {
    txBody.innerHTML = '<tr class="empty-row"><td colspan="5" class="empty-state">No transactions yet</td></tr>';
    return;
  }

  txBody.innerHTML = appState.trades.map((tx, i) => `
    <tr>
      <td>${new Date(tx.timestamp).toLocaleDateString()}</td>
      <td>${tx.type === 'buy' ? 'Purchase' : 'Sale'}</td>
      <td>${tx.units} units</td>
      <td><span style="color: #28a745;">Completed</span></td>
      <td><code style="font-size: 10px;">0x${Math.random().toString(16).substring(2, 10)}</code></td>
    </tr>
  `).join('');
}

// ============================================
// KYC & WALLET
// ============================================

async function submitKYC(event) {
  event.preventDefault();

  const name = document.getElementById('kyc-name').value;
  const email = document.getElementById('kyc-email').value;
  const accreditation = document.getElementById('kyc-accreditation').value;

  // Mock KYC approval
  appState.kyc = {
    status: 'approved',
    provider_ref: `kyc_${Date.now()}`,
    name,
    email,
    accreditation
  };

  showSuccess('KYC verification submitted successfully!');
  closeModal('kyc-modal');
  updateKYCBadge();
  loadAccountData();
}

async function linkWallet(event) {
  event.preventDefault();

  const address = document.getElementById('wallet-input').value;
  const custodyType = document.getElementById('custody-type').value;

  if (!address.startsWith('r')) {
    showError('Invalid XRPL address');
    return;
  }

  appState.wallet = {
    address,
    custody_type: custodyType,
    trustlines: 2 // Mock trustlines
  };

  showSuccess('Wallet linked successfully!');
  closeModal('wallet-modal');
  loadAccountData();
}

// ============================================
// UTILITIES
// ============================================

function showError(message) {
  console.error(message);
  const alert = document.createElement('div');
  alert.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #dc3545;
    color: white;
    padding: 16px 24px;
    border-radius: 8px;
    z-index: 2000;
    animation: slideIn 0.3s ease;
  `;
  alert.textContent = message;
  document.body.appendChild(alert);
  setTimeout(() => alert.remove(), 4000);
}

function showSuccess(message) {
  const alert = document.createElement('div');
  alert.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #28a745;
    color: white;
    padding: 16px 24px;
    border-radius: 8px;
    z-index: 2000;
    animation: slideIn 0.3s ease;
  `;
  alert.textContent = message;
  document.body.appendChild(alert);
  setTimeout(() => alert.remove(), 4000);
}

// ============================================
// CHATBOT FUNCTIONALITY
// ============================================

let chatHistory = [];

function toggleChatbot() {
  const panel = document.getElementById('chatbot-panel');
  if (panel) {
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    if (panel.style.display === 'block' && chatHistory.length === 0) {
      appendChatMessage('👋 Hi! I\'m here to help with questions about Eigenrestarea. Ask me about properties, valuations, trading, or how to invest.', 'assistant');
    }
  }
}

async function sendChatMessage() {
  const input = document.getElementById('chatbot-input');
  const message = input.value.trim();
  
  if (!message) return;
  
  // Display user message
  appendChatMessage(message, 'user');
  input.value = '';
  
  try {
    const response = await apiFetch('/chatbot/ask', {
      method: 'POST',
      body: JSON.stringify({
        message: message,
        user_id: appState.currentUser?.id
      })
    });
    
    appendChatMessage(response.response, 'assistant');
  } catch (error) {
    console.error('Chatbot error:', error);
    appendChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
  }
}

function appendChatMessage(text, role) {
  const container = document.getElementById('chatbot-messages');
  if (!container) return;
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;
  
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  
  // Check if text contains recommendations (JSON-like structure)
  if (typeof text === 'object' && text.recommendations) {
    bubble.innerHTML = renderRecommendations(text.recommendations);
  } else {
    bubble.textContent = text;
  }
  
  messageDiv.appendChild(bubble);
  container.appendChild(messageDiv);
  container.scrollTop = container.scrollHeight;
  
  chatHistory.push({ role, message: text });
}

function renderRecommendations(recommendations) {
  if (!recommendations || recommendations.length === 0) {
    return '<p>No properties found matching your criteria.</p>';
  }
  
  let html = '<div class="recommendations-container">';
  html += `<h4>✨ Recommended Properties (${recommendations.length})</h4>`;
  
  recommendations.forEach((rec, idx) => {
    html += `
      <div class="recommendation-card">
        <div class="recommendation-header">
          <h5>${rec.block} ${rec.street}, ${rec.town}</h5>
          <span class="price">SGD ${rec.price_sgd?.toLocaleString('en-SG', {maximumFractionDigits: 0}) || 'TBD'}</span>
        </div>
        <div class="recommendation-details">
          <p>• ${rec.flat_type} | ${rec.area_sqm}m² | Lease: ${rec.remaining_lease}</p>
          <p class="reason">💡 ${rec.reason}</p>
        </div>
        <button class="buy-btn" onclick="prefilBuyModal('${rec.property_id}', ${rec.price_sgd})">
          🛒 Buy Now
        </button>
      </div>
    `;
  });
  
  html += '</div>';
  return html;
}

async function askForRecommendations() {
  // Trigger chatbot to ask user for budget
  const message = "What's your budget in SGD? (e.g., 500000 or 600000)";
  appendChatMessage(message, 'assistant');
}

async function getRecommendations(budgetSgd, riskProfile = 'medium') {
  try {
    const response = await apiFetch('/chatbot/recommend', {
      method: 'POST',
      body: JSON.stringify({
        budget_sgd: budgetSgd,
        risk_profile: riskProfile,
        limit: 5
      })
    });
    
    // Display recommendations in chatbot
    const message = `I found ${response.recommendations.length} properties for you:`;
    appendChatMessage(message, 'assistant');
    appendChatMessage(response, 'assistant');
    
  } catch (error) {
    console.error('Recommendation error:', error);
    appendChatMessage('Sorry, I couldn\'t get recommendations at the moment. Try again later.', 'assistant');
  }
}

function prefilBuyModal(propertyId, price) {
  // Pre-fill the buy modal with property details
  openModal('trade-modal');
  document.getElementById('property-select').value = propertyId;
  document.getElementById('trade-price').value = price;
  document.getElementById('unit-count').value = 1;
}

// ============================================
// EXPLAINABILITY – SHAP-based Price Breakdown
// ============================================

async function loadExplanation(property) {
  if (!property) return;
  
  const payload = {
    town: property.town,
    flat_type: property.flat_type,
    block: property.block || '',
    street_name: property.street_name || '',
    floor_area_sqm: property.floor_area_sqm,
    storey_range: property.storey_range,
    lease_commence_date: property.lease_commence_date ? `${property.lease_commence_date}-01-01` : '1985-01-01',
    remaining_lease: property.remaining_lease || '60 years',
    txn_date: new Date().toISOString().split('T')[0]
  };
  
  try {
    const response = await apiFetch('/avm/predict-with-explanation', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    
    const explanationSection = document.getElementById('explanation-section');
    if (explanationSection && response.explanation) {
      explanationSection.style.display = 'block';
      
      // Update base price
      const basePriceEl = document.getElementById('base-value');
      if (basePriceEl && response.explanation.base_price) {
        basePriceEl.textContent = response.explanation.base_price.toLocaleString('en-SG', {
          style: 'currency',
          currency: 'SGD',
          minimumFractionDigits: 0
        });
      }
      
      // Render SHAP contribution bars
      const container = document.getElementById('feature-bars');
      if (container) {
        container.innerHTML = '';
        response.explanation.feature_contributions.slice(0, 10).forEach(contrib => {
          const bar = document.createElement('div');
          bar.className = 'shap-bar';
          
          const isPositive = contrib.contribution > 0;
          const barColor = isPositive ? 'shap-bar-positive' : 'shap-bar-negative';
          const width = Math.min(Math.abs(contrib.contribution) / 10000 * 200, 200);
          
          const label = document.createElement('div');
          label.className = 'shap-bar-label';
          label.textContent = contrib.feature_name;
          
          const barDiv = document.createElement('div');
          barDiv.className = barColor;
          barDiv.style.width = width + 'px';
          
          const value = document.createElement('div');
          value.style.marginLeft = '10px';
          value.textContent = (contrib.contribution > 0 ? '+' : '') + contrib.contribution.toLocaleString('en-SG', {
            style: 'currency',
            currency: 'SGD',
            minimumFractionDigits: 0
          });
          
          bar.appendChild(label);
          bar.appendChild(barDiv);
          bar.appendChild(value);
          container.appendChild(bar);
        });
      }
      
      // Update confidence band
      const confLower = document.getElementById('conf-lower');
      const confUpper = document.getElementById('conf-upper');
      if (confLower && confUpper) {
        confLower.textContent = response.confidence_lower.toLocaleString('en-SG', {
          style: 'currency',
          currency: 'SGD',
          minimumFractionDigits: 0
        });
        confUpper.textContent = response.confidence_upper.toLocaleString('en-SG', {
          style: 'currency',
          currency: 'SGD',
          minimumFractionDigits: 0
        });
      }
      
      // Add market card after explanation loads
      if (property && property.avm_value) {
        const marketHTML = renderMarketCard(property.avm_value);
        explanationSection.insertAdjacentHTML('afterend', marketHTML);
      }
    }
  } catch (error) {
    console.error('Failed to load explanation:', error);
  }
}

// ============================================
// XRPL INTEGRATION
// ============================================

let xrplLedgerIndex = 0;
let xrplActivityFeed = [];

// Initialize XRPL features
function initXRPLFeatures() {
  startLedgerHeartbeat();
  startActivityFeed();
}

// XRPL Proof Bar - Simulated ledger heartbeat
function startLedgerHeartbeat() {
  // Simulate ledger closing every 3-4 seconds
  setInterval(() => {
    xrplLedgerIndex += 1;
    const proofLedger = document.getElementById('proof-ledger');
    if (proofLedger) {
      proofLedger.textContent = `#${xrplLedgerIndex.toLocaleString()}`;
    }
    
    // Pulse the heartbeat
    const heartbeat = document.getElementById('proof-heartbeat');
    if (heartbeat) {
      heartbeat.style.animation = 'none';
      setTimeout(() => {
        heartbeat.style.animation = 'heartbeat-pulse 2s infinite';
      }, 10);
    }
  }, 3500);

  // Set initial values
  const network = document.getElementById('proof-network');
  if (network) network.textContent = 'Testnet';
  
  xrplLedgerIndex = Math.floor(Math.random() * 1000000) + 75000000;
  const proofLedger = document.getElementById('proof-ledger');
  if (proofLedger) proofLedger.textContent = `#${xrplLedgerIndex.toLocaleString()}`;
}

// Transaction Receipt Drawer
function showTransactionReceipt(transactions = []) {
  const drawer = document.getElementById('tx-receipt-drawer');
  const stepsContainer = document.getElementById('tx-receipt-steps');
  
  if (!stepsContainer) return;
  
  stepsContainer.innerHTML = '';
  
  // Default transactions if none provided
  if (transactions.length === 0) {
    transactions = [
      { title: 'Trustline Created', status: 'validated', hash: '3A' + generateMockHash() },
      { title: 'Payment Sent (XRP)', status: 'validated', hash: '5F' + generateMockHash() },
      { title: 'SGPROP Delivered', status: 'pending', hash: '7E' + generateMockHash() }
    ];
  }
  
  transactions.forEach((tx, idx) => {
    setTimeout(() => {
      const stepEl = createTransactionStep(tx);
      stepsContainer.appendChild(stepEl);
    }, idx * 500);
  });
  
  drawer?.classList.add('active');
}

function createTransactionStep(tx) {
  const div = document.createElement('div');
  div.className = `tx-step ${tx.status === 'validated' ? 'completed' : 'pending'}`;
  
  const icon = tx.status === 'validated' ? '✓' : '⏳';
  const statusText = tx.status === 'validated' ? 'Validated' : 'Submitted';
  
  div.innerHTML = `
    <div class="tx-step-icon">${icon}</div>
    <div class="tx-step-content">
      <div class="tx-step-title">${tx.title}</div>
      <div class="tx-step-hash">TX: ${tx.hash}</div>
      <div class="tx-step-status">${statusText}</div>
      <a href="javascript:void(0)" class="tx-step-link" onclick="alert('View on explorer: xrpl.ws')">View on Explorer</a>
    </div>
  `;
  
  return div;
}

function closeTxReceipt() {
  const drawer = document.getElementById('tx-receipt-drawer');
  if (drawer) drawer.classList.remove('active');
}

// Trustline Handshake Animation (during KYC approval)
function showTrustlineHandshake() {
  const modal = document.getElementById('trustline-handshake-modal');
  if (modal) {
    modal.classList.add('active');
    
    // Simulate trustline creation
    setTimeout(() => {
      const status = document.getElementById('trustline-status');
      const badge = document.getElementById('trustline-badge');
      if (status) status.textContent = 'Trustline authorized!';
      if (badge) badge.style.display = 'block';
      
      // Auto-close after 2 seconds
      setTimeout(() => {
        modal.classList.remove('active');
      }, 2000);
    }, 1500);
  }
}

// Activity Feed - Simulated XRPL events
function startActivityFeed() {
  addActivityItem('🔗 Connected to XRPL Testnet', 'Ledger: #75000000');
  
  setInterval(() => {
    const events = [
      { title: '📝 Offer Created', detail: 'SGPROP/XRP trading pair' },
      { title: '💰 Payment Received', detail: '5000 XRP from liquidity pool' },
      { title: '✅ Trustline Authorized', detail: 'SGPROP tokens now holdable' },
      { title: '📊 Price Updated', detail: 'SGPROP/XRP: 0.0085 XRP' }
    ];
    
    const randomEvent = events[Math.floor(Math.random() * events.length)];
    addActivityItem(randomEvent.title, randomEvent.detail);
  }, 6000);
}

function addActivityItem(title, detail) {
  const feed = document.getElementById('activity-feed');
  if (!feed) return;
  
  const item = document.createElement('div');
  item.className = 'activity-item';
  const now = new Date().toLocaleTimeString();
  
  item.innerHTML = `
    <div class="activity-item-time">${now}</div>
    <div class="activity-item-text">${title}</div>
    <div class="activity-item-detail">${detail}</div>
  `;
  
  feed.insertBefore(item, feed.firstChild);
  
  // Keep feed size limited
  while (feed.children.length > 20) {
    feed.removeChild(feed.lastChild);
  }
  
  xrplActivityFeed.unshift({ title, detail, time: now });
}

// SGPROP/XRP Market Card (show on property detail)
function renderMarketCard(propertyPrice) {
  const xrpPrice = propertyPrice / 5000; // Mock: 1 SGPROP ≈ 5000 SGD = ~60 XRP
  const spread = xrpPrice * 0.02;
  
  return `
    <div class="market-card">
      <div class="market-header">
        <h4>SGPROP/XRP Market</h4>
        <span class="market-live-badge">● LIVE</span>
      </div>
      <div class="market-price">
        <div class="market-price-item">
          <div class="market-price-label">Buy Price</div>
          <div class="market-price-value">${(xrpPrice + spread).toFixed(4)} XRP</div>
        </div>
        <div class="market-price-item">
          <div class="market-price-label">Sell Price</div>
          <div class="market-price-value">${(xrpPrice - spread).toFixed(4)} XRP</div>
        </div>
      </div>
      <div class="market-source">
        <small>💧 Liquidity: XRPL AMM / DEX Offers</small>
      </div>
    </div>
  `;
}

// Helper: Generate mock tx hash
function generateMockHash() {
  return Array.from({ length: 56 }, () => 
    '0123456789ABCDEF'[Math.floor(Math.random() * 16)]
  ).join('').toUpperCase();
}

// Start XRPL features on page load
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => initXRPLFeatures(), 1000);
});

