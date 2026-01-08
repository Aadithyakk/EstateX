const BASE = (window.BASE_URL || 'http://localhost:8000')

async function health() {
  const res = await fetch(`${BASE}/health`)
  const txt = await res.text()
  document.getElementById('health-out').textContent = txt
}

async function avmPredict(formData) {
  const body = Object.fromEntries(formData)
  const res = await fetch(`${BASE}/avm/predict`, {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
  })
  const json = await res.json()
  document.getElementById('avm-out').textContent = JSON.stringify(json, null, 2)
}

async function createProperty(formData) {
  const body = Object.fromEntries(formData)
  const res = await fetch(`${BASE}/properties/`, {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
  })
  const json = await res.json()
  document.getElementById('prop-out').textContent = JSON.stringify(json, null, 2)
}

async function getQuote(offeringId, side, qty) {
  const url = new URL(`${BASE}/quote/`)
  url.searchParams.set('offering_id', offeringId)
  url.searchParams.set('side', side)
  url.searchParams.set('qty', qty)
  const res = await fetch(url.toString())
  const json = await res.json()
  document.getElementById('quote-out').textContent = JSON.stringify(json, null, 2)
}

document.getElementById('btn-health').addEventListener('click', health)

document.getElementById('avm-form').addEventListener('submit', (e)=>{
  e.preventDefault()
  avmPredict(new FormData(e.target))
})

document.getElementById('prop-form').addEventListener('submit', (e)=>{
  e.preventDefault()
  createProperty(new FormData(e.target))
})

document.getElementById('btn-quote').addEventListener('click', ()=>{
  const offering = document.getElementById('quote-offering').value
  const side = document.getElementById('quote-side').value
  const qty = document.getElementById('quote-qty').value
  getQuote(offering, side, qty)
})
