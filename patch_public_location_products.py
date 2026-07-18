#!/usr/bin/env python3
"""Add Seabrook property rules and location-resolved products to public booking site."""
from pathlib import Path
import shutil, sys

PATH = Path('index.html')
MARKER = '[location-products-public-v1]'
if not PATH.exists():
    sys.exit('ERROR: index.html not found; run from golfcart-booking repo root')
src = PATH.read_text(encoding='utf-8')
if MARKER in src:
    print('SKIP: public location/products patch already applied')
    sys.exit(0)

def rep(old, new, label):
    global src
    n = src.count(old)
    if n != 1:
        sys.exit(f'ANCHOR ERROR [{label}]: expected 1, found {n}')
    src = src.replace(old, new, 1)
    print(f'  ok: {label}')

# CSS
old = '''  .zone-fee { font-size: 11px; color: var(--muted); font-weight: 600; }
  .zone-pill.selected .zone-fee { color: var(--brand); }
'''
new = old + '''
  /* [location-products-public-v1] */
  .location-rule { display:none; margin-top:12px; padding:11px 13px; border-radius:10px; font-size:13px; line-height:1.45; font-weight:600; }
  .location-rule.info { display:block; background:#e3f2fd; border:1px solid #90caf9; color:#0d47a1; }
  .location-rule.warn { display:block; background:#fff8e1; border:1px solid #ffd54f; color:#8a4b00; }
  .location-rule.block { display:block; background:#ffebee; border:1px solid #ef9a9a; color:#b71c1c; }
  .property-help { margin-top:6px; font-size:11px; color:var(--muted); }
  .ack-box { display:none; margin-top:10px; padding:10px 12px; border-radius:10px; background:#fff8e1; border:1px solid #ffd54f; }
  .ack-box.visible { display:flex; align-items:flex-start; gap:9px; }
  .ack-box input { width:18px; height:18px; margin-top:1px; accent-color:var(--brand); }
  .ack-box label { font-size:12px; color:#8a4b00; font-weight:650; line-height:1.4; cursor:pointer; }
'''
rep(old, new, 'add location rule styles')

# Insert Seabrook property selector immediately before Delivery Address group.
old = '''      <div class="form-group" style="margin-bottom:14px;">
        <label class="form-label">Delivery Address</label>
'''
new = '''      <div class="form-group" id="seabrook-property-group" style="display:none;margin-bottom:14px;">
        <label class="form-label">Which Seabrook property?</label>
        <select id="property-select" onchange="onPropertyChange()">
          <option value="">-- Select property --</option>
          <optgroup label="Normal / Special">
            <option>Other / Private Home</option>
            <option>Sealoft Villas</option>
          </optgroup>
          <optgroup label="Gas Cart Required">
            <option>Beach Club</option><option>Chateau By The Green</option><option>Creekwatch</option>
            <option>Dunecrest</option><option>Duneloft</option><option>Live Oak</option><option>Marsh Walk</option>
            <option>Ocean Winds</option><option>Shelter Cove</option><option>St. Christopher Oaks</option><option>Treeloft</option>
          </optgroup>
          <optgroup label="No LSV Rentals">
            <option>Atrium Villas</option><option>Bay Point</option><option>Bohicket Marina Village</option>
            <option>Golf Shore</option><option>Heron Point</option><option>High Hammock Village (Villas)</option>
            <option>Pelican Watch</option><option>Racquet Club</option><option>Wedgewood</option>
          </optgroup>
        </select>
        <div class="property-help">The property determines whether an electric cart, gas cart, or no rental is permitted.</div>
      </div>
      <div class="form-group" style="margin-bottom:14px;">
        <label class="form-label">Delivery Address</label>
'''
rep(old, new, 'add Seabrook property dropdown')

old = '''        <input type="text" id="addr-input" oninput="checkStep3()" placeholder="123 Pelican Bay Dr, Seabrook Island, SC 29455" />
      </div>
      <div class="form-group">
'''
new = '''        <input type="text" id="addr-input" oninput="checkStep3()" placeholder="123 Pelican Bay Dr, Seabrook Island, SC 29455" />
        <div id="location-rule" class="location-rule"></div>
        <div id="location-ack" class="ack-box">
          <input type="checkbox" id="location-ack-input" onchange="onLocationAckChange()" />
          <label for="location-ack-input">I understand that at Sealoft Villas an electric cart must be charged in the driveway, never underneath the house, and GolfCart.Fun does not provide an extension cord.</label>
        </div>
      </div>
      <div class="form-group">
'''
rep(old, new, 'add rule message and acknowledgment')

rep('''  zone: null,
  delivery_fee: 0,
  delivery_address: null,
''', '''  zone: null,
  property_name: null,
  location_acknowledged: false,
  location_allowed: false,
  location_rule: null,
  resolved_cart_type: null,
  delivery_fee: 0,
  delivery_address: null,
''', 'extend public booking state')

rep('''    const res = await fetch(`${API}/pricing/public`);
''', '''    const res = await fetch(`${API}/pricing/public?ts=${Date.now()}`, { cache: 'no-store' });
''', 'load uncached pricing')

rep('''  if (n > 3 && (!state.zone || !state.delivery_address)) return;
''', '''  if (n > 3 && (!state.zone || !state.delivery_address || !state.location_allowed)) return;
''', 'require resolved location before checkout')

rep('''  if (document.getElementById('date-input').value) populateDurations();
}
''', '''  if (document.getElementById('date-input').value) populateDurations();
  if (state.zone) checkStep3();
}
''', 'recheck location after cart change')

old = '''function selectZone(name, fee, el) {
  state.zone = name;
  state.delivery_fee = fee;
  document.querySelectorAll('.zone-pill').forEach(p => p.classList.remove('selected'));
  el.classList.add('selected');
  checkStep3();
}
function checkStep3() {
  const addr = document.getElementById('addr-input').value.trim();
  state.delivery_address = addr.length > 5 ? addr : null;
  document.getElementById('next3').disabled = !(state.zone && state.delivery_address);
}
'''
new = '''function selectZone(name, fee, el) {
  state.zone = name;
  state.delivery_fee = fee;
  state.property_name = null;
  state.location_acknowledged = false;
  state.location_allowed = false;
  state.location_rule = null;
  state.resolved_cart_type = null;
  document.querySelectorAll('.zone-pill').forEach(p => p.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('seabrook-property-group').style.display = name === 'Seabrook Island' ? 'block' : 'none';
  document.getElementById('property-select').value = '';
  document.getElementById('location-ack-input').checked = false;
  renderLocationRule(null);
  checkStep3();
}
function onPropertyChange() {
  state.property_name = document.getElementById('property-select').value || null;
  state.location_acknowledged = false;
  document.getElementById('location-ack-input').checked = false;
  checkStep3();
}
function onLocationAckChange() {
  state.location_acknowledged = document.getElementById('location-ack-input').checked;
  checkStep3();
}
function displayProductName(key) {
  if (key === '4seat') return '4-Passenger LSV';
  if (key === '6seat_gas') return '6-Seat Gas LSV';
  if (key === '6seat_wild_dunes') return '6-Seat Wild Dunes LSV';
  return '6-Passenger LSV';
}
function renderLocationRule(rule) {
  const box = document.getElementById('location-rule');
  const ack = document.getElementById('location-ack');
  ack.className = 'ack-box' + (rule && rule.requires_ack ? ' visible' : '');
  if (!rule || !rule.message) {
    box.className = 'location-rule';
    box.textContent = '';
    return;
  }
  const cls = !rule.allowed && !rule.requires_ack ? 'block' : rule.rule === 'sealoft' ? 'warn' : 'info';
  box.className = `location-rule ${cls}`;
  const assigned = rule.resolved_cart_type && rule.resolved_cart_type !== state.cart_type
    ? ` Assigned cart: ${displayProductName(rule.resolved_cart_type)}.` : '';
  box.textContent = rule.message + assigned;
}
let locationTimer = null;
function checkStep3() {
  const addr = document.getElementById('addr-input').value.trim();
  state.delivery_address = addr.length > 5 ? addr : null;
  if (state.zone === 'Seabrook Island') state.property_name = document.getElementById('property-select').value || null;
  const baseReady = !!(state.zone && state.delivery_address && state.cart_type && state.start_date && state.duration_days && (state.zone !== 'Seabrook Island' || state.property_name));
  state.location_allowed = false;
  document.getElementById('next3').disabled = true;
  clearTimeout(locationTimer);
  if (!baseReady) {
    renderLocationRule(null);
    return;
  }
  locationTimer = setTimeout(async () => {
    try {
      const p = new URLSearchParams({
        zone: state.zone || '',
        property_name: state.property_name || '',
        address: state.delivery_address || '',
        cart_type: state.cart_type || '',
        location_acknowledged: String(!!state.location_acknowledged),
      });
      const res = await fetch(`${API}/bookings/check-address?${p}`);
      const rule = await res.json();
      state.location_rule = rule;
      state.resolved_cart_type = rule.resolved_cart_type || state.cart_type;
      renderLocationRule(rule);
      if (!rule.allowed) return;

      const ap = new URLSearchParams({
        start_date: state.start_date,
        duration_days: state.duration_days,
        cart_type: state.resolved_cart_type || state.cart_type,
        zone: state.zone || '',
        property_name: state.property_name || '',
        delivery_address: state.delivery_address || '',
        location_acknowledged: String(!!state.location_acknowledged),
      });
      const ar = await fetch(`${API}/bookings/availability?${ap}`);
      const availability = await ar.json();
      state.avail = availability;
      state.location_allowed = !!availability.available;
      if (!availability.available) {
        renderLocationRule({ allowed:false, rule:'inventory', message: availability.error || `No ${displayProductName(state.resolved_cart_type)} carts are available for those dates.` });
      }
      document.getElementById('next3').disabled = !state.location_allowed;
    } catch (e) {
      renderLocationRule({ allowed:false, rule:'error', message:'We could not verify this location. Please try again or call (843) 800-0310.' });
    }
  }, 350);
}
'''
rep(old, new, 'resolve property rules and product availability')

rep('''    const cartLabel = qty > 1
      ? `${qty}x ${state.duration_days}-day ${state.cart_type==='4seat'?'4-Passenger':'6-Passenger'}`
      : `${state.duration_days}-day ${state.cart_type==='4seat'?'4-Passenger':'6-Passenger'}`;
''', '''    const shownProduct = displayProductName(state.resolved_cart_type || state.cart_type).replace(' LSV','');
    const cartLabel = qty > 1
      ? `${qty}x ${state.duration_days}-day ${shownProduct}`
      : `${state.duration_days}-day ${shownProduct}`;
''', 'show resolved product in order summary')

rep('''        zone:                 state.zone,
        delivery_address:     state.delivery_address,
''', '''        zone:                 state.zone,
        property_name:        state.property_name,
        location_acknowledged: !!state.location_acknowledged,
        delivery_address:     state.delivery_address,
''', 'send location fields to checkout')

backup = PATH.with_suffix('.html.bak')
shutil.copy2(PATH, backup)
PATH.write_text(src, encoding='utf-8')
print('DONE: patched index.html')
