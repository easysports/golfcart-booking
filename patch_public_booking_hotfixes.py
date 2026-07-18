#!/usr/bin/env python3
from pathlib import Path
import shutil, sys
P=Path('index.html'); MARK='[booking-flow-hotfix-v1]'
if not P.exists(): sys.exit('ERROR: index.html not found')
s=P.read_text()
if MARK in s: print('SKIP: already applied'); sys.exit(0)
def rep(old,new,label):
 global s
 c=s.count(old)
 if c!=1: sys.exit(f'ANCHOR ERROR {label}: {c}')
 s=s.replace(old,new,1); print('  ok:',label)

rep('''      <div class="form-group" id="seabrook-property-group" style="display:none;margin-bottom:14px;">
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
''','''      <!-- [booking-flow-hotfix-v1] Address matching is the source of truth. -->
      <div class="form-group" id="seabrook-property-group" style="display:none;margin-bottom:14px;">
        <div style="padding:12px 14px;border:1px solid #b3e5fc;background:#f3fbff;border-radius:12px;font-size:12px;line-height:1.55;color:var(--sub);">
          <strong style="color:var(--text);">Seabrook delivery rules</strong><br>
          Enter the full delivery address. We automatically recognize the neighborhood, including close spellings.<br>
          <strong>Gas cart required:</strong> Beach Club, Chateau By The Green, Creekwatch, Dunecrest, Duneloft, Live Oak, Marsh Walk, Ocean Winds, Shelter Cove, St. Christopher Oaks and Treeloft.<br>
          <strong>No LSV rentals:</strong> Atrium Villas, Bay Point, Bohicket Marina Village, Golf Shore, Heron Point, High Hammock, Pelican Watch, Racquet Club and Wedgewood.<br>
          <strong>Sealoft Villas:</strong> electric or gas is allowed; electric carts must charge in the driveway, never under the house. We do not provide an extension cord and recommend gas.
        </div>
      </div>
''','replace required property dropdown with address rules note')

rep('''        <div id="location-rule" class="location-rule"></div>
        <div id="location-ack" class="ack-box">
''','''        <div id="location-rule" class="location-rule"></div>
        <div id="location-availability" class="location-rule"></div>
        <div id="location-ack" class="ack-box">
''','add separate location availability message')

rep('''function fmtMoney(n) {
  return '$' + parseFloat(n).toLocaleString('en-US', { minimumFractionDigits:2, maximumFractionDigits:2 });
}
''','''function fmtMoney(n) {
  return '$' + parseFloat(n).toLocaleString('en-US', { minimumFractionDigits:2, maximumFractionDigits:2 });
}
function localISODate(date) {
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
}
function tomorrowISODate() {
  const d = new Date(); d.setHours(12,0,0,0); d.setDate(d.getDate()+1); return localISODate(d);
}
function selectedProductLabel(key = state.cart_type) {
  return key === '4seat' ? '4-Passenger' : key === '6seat_gas' ? '6-Seat Gas' : key === '6seat_wild_dunes' ? '6-Seat Wild Dunes' : '6-Passenger';
}
function selectedDateRange() {
  if (!state.start_date || !state.duration_days) return '';
  return `${fmtDate(state.start_date)} – ${fmtDate(addDays(state.start_date, state.duration_days))}`;
}
const BOOKING_DRAFT_KEY = 'gcf_checkout_draft_v1';
function readBookingDraft() {
  try {
    const draft = JSON.parse(sessionStorage.getItem(BOOKING_DRAFT_KEY) || 'null');
    return draft && Date.now() - Number(draft.saved_at || 0) < 6 * 60 * 60 * 1000 ? draft : null;
  } catch { return null; }
}
function saveBookingDraft(checkoutStarted = false) {
  try {
    const fields = {};
    ['fname','lname','email','phone','notes','arrival-input','addr-input'].forEach(id => { const el=document.getElementById(id); if(el) fields[id]=el.value; });
    fields['sms-opt'] = !!document.getElementById('sms-opt')?.checked;
    fields['terms-check'] = !!document.getElementById('terms-check')?.checked;
    sessionStorage.setItem(BOOKING_DRAFT_KEY, JSON.stringify({ saved_at:Date.now(), checkout_started:checkoutStarted, state:{...state}, fields }));
  } catch {}
}
function clearBookingDraft() { try { sessionStorage.removeItem(BOOKING_DRAFT_KEY); } catch {} }
''','add date labels and checkout draft helpers')

rep("""  if (n > 2 && (!state.duration_days || !state.avail?.available)) return;
""","""  if (n > 2 && !state.duration_days) return;
""",'do not block dates before location-specific availability')

rep('''function populateDurations() {
  const dateStr = document.getElementById('date-input').value;
''','''function populateDurations() {
  const dateStr = document.getElementById('date-input').value;
  if (dateStr) state.start_date = dateStr;
''','sync browser-restored date into state')

start=s.index('function onDateChange() {')
end=s.index('// ── STEP 3', start)
old=s[start:end]
new='''function onDateChange() {
  state.start_date = document.getElementById('date-input').value;
  state.duration_days = null;
  state.avail = null;
  document.getElementById('avail-bar').className = 'avail-bar';
  document.getElementById('price-preview').className = 'price-preview';
  document.getElementById('next2').disabled = true;
  populateDurations();
}

let availTimer = null;
function onDurChange() {
  state.start_date = document.getElementById('date-input').value || state.start_date;
  const val = document.getElementById('dur-select').value;
  state.duration_days = val ? parseInt(val) : null;
  state.avail = null;
  document.getElementById('next2').disabled = true;

  if (!val || !state.start_date) {
    document.getElementById('avail-bar').className = 'avail-bar';
    document.getElementById('price-preview').className = 'price-preview';
    return;
  }

  const s = getSeason(state.start_date, state.cart_type);
  if (!s) return;
  const durRecord = getPriceForDuration(s.id, state.cart_type, state.duration_days);
  if (!durRecord || durRecord.price === null) return;
  state.base_price = durRecord.price;
  state.season = s.name;
  updatePricePreview();
  document.getElementById('price-preview').className = 'price-preview visible';

  // The actual inventory pool depends on the delivery address (standard, gas,
  // or Wild Dunes), so Step 2 confirms the selection and Step 3 verifies stock.
  const bar = document.getElementById('avail-bar');
  bar.className = 'avail-bar ok';
  bar.style.display = '';
  bar.textContent = `✅ ${selectedProductLabel()} selected · ${selectedDateRange()} · final availability checked after delivery address`;
  state.avail = { available: true, preliminary: true };
  document.getElementById('next2').disabled = false;
  saveBookingDraft(false);
}

'''
s=s[:start]+new+s[end:]
print('  ok: fix duration continuation and show selected cart/date')

rep('''  document.getElementById('seabrook-property-group').style.display = name === 'Seabrook Island' ? 'block' : 'none';
  document.getElementById('property-select').value = '';
  document.getElementById('location-ack-input').checked = false;
''','''  document.getElementById('seabrook-property-group').style.display = name === 'Seabrook Island' ? 'block' : 'none';
  document.getElementById('location-ack-input').checked = false;
''','remove property select reset')

# Remove unused property handler safely
old='''function onPropertyChange() {
  state.property_name = document.getElementById('property-select').value || null;
  state.location_acknowledged = false;
  document.getElementById('location-ack-input').checked = false;
  checkStep3();
}
'''
if s.count(old)!=1: sys.exit(f'ANCHOR ERROR property handler: {s.count(old)}')
s=s.replace(old,'',1); print('  ok: remove property dropdown handler')

rep('''  if (state.zone === 'Seabrook Island') state.property_name = document.getElementById('property-select').value || null;
  const baseReady = !!(state.zone && state.delivery_address && state.cart_type && state.start_date && state.duration_days && (state.zone !== 'Seabrook Island' || state.property_name));
''','''  state.property_name = null;
  const baseReady = !!(state.zone && state.delivery_address && state.cart_type && state.start_date && state.duration_days);
''','use address as source of truth')

# Replace checkStep3 async body so rule and availability are separate
old='''      state.location_rule = rule;
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
'''
new='''      state.location_rule = rule;
      state.resolved_cart_type = rule.resolved_cart_type || state.cart_type;
      renderLocationRule(rule);
      const availabilityBox = document.getElementById('location-availability');
      availabilityBox.className = 'location-rule';
      availabilityBox.textContent = '';
      if (!rule.allowed) return;

      const ap = new URLSearchParams({
        start_date: state.start_date,
        duration_days: state.duration_days,
        cart_type: state.resolved_cart_type || state.cart_type,
        zone: state.zone || '',
        delivery_address: state.delivery_address || '',
        location_acknowledged: String(!!state.location_acknowledged),
      });
      const ar = await fetch(`${API}/bookings/availability?${ap}`);
      const availability = await ar.json();
      state.avail = availability;
      state.location_allowed = !!availability.available;
      const label = displayProductName(state.resolved_cart_type || state.cart_type).replace(' LSV','');
      const range = selectedDateRange();
      if (availability.available) {
        availabilityBox.className = 'location-rule info';
        availabilityBox.textContent = `✅ ${label} selected · ${range} · ${availability.available_count} available`;
      } else {
        availabilityBox.className = 'location-rule block';
        availabilityBox.textContent = availability.error || `No ${label} carts are available for ${range}.`;
      }
      document.getElementById('next3').disabled = !state.location_allowed;
      saveBookingDraft(false);
'''
if s.count(old)!=1: sys.exit(f'ANCHOR ERROR location availability: {s.count(old)}')
s=s.replace(old,new,1); print('  ok: keep Beach Club rule visible and show live inventory/date')

rep('''        property_name:        state.property_name,
        location_acknowledged: !!state.location_acknowledged,
''','''        property_name:        null,
        location_acknowledged: !!state.location_acknowledged,
        return_url:            `${window.location.origin}${window.location.pathname}`,
''','send return URL and rely on address matching')

rep('''      state.checkoutUrl = data.checkout_url;
      document.getElementById('link-ready').classList.add('visible');
''','''      state.checkoutUrl = data.checkout_url;
      saveBookingDraft(true);
      document.getElementById('link-ready').classList.add('visible');
''','save booking before Stripe redirect')

rep("""document.getElementById('date-input').min = new Date().toISOString().split('T')[0];
""","""const firstBookableDate = tomorrowISODate();
document.getElementById('date-input').min = firstBookableDate;
document.getElementById('date-input').value = firstBookableDate;
state.start_date = firstBookableDate;
""",'default booking calendar to tomorrow')

# Insert restoration function before init
anchor='''// ── INIT ─────────────────────────────────────────────────────────────────────
'''
restore='''function restoreCheckoutDraft() {
  const draft = readBookingDraft();
  if (!draft?.checkout_started || !draft.state?.cart_type) return false;
  const saved = draft.state;
  selectCart(saved.cart_type);
  selectQty(Number(saved.quantity) || 1);
  document.getElementById('date-input').value = saved.start_date || firstBookableDate;
  state.start_date = saved.start_date || firstBookableDate;
  populateDurations();
  if (saved.duration_days) {
    document.getElementById('dur-select').value = String(saved.duration_days);
    onDurChange();
  }
  if (saved.zone) {
    const pill = [...document.querySelectorAll('.zone-pill')].find(el => el.textContent.trim().startsWith(saved.zone));
    if (pill) selectZone(saved.zone, Number(saved.delivery_fee) || 99.99, pill);
  }
  state = { ...state, ...saved, location_allowed:true, avail:saved.avail || {available:true} };
  const fields = draft.fields || {};
  Object.entries(fields).forEach(([id,value]) => {
    const el=document.getElementById(id); if(!el) return;
    if (el.type === 'checkbox') el.checked = !!value; else el.value = value ?? '';
  });
  state.delivery_address = fields['addr-input'] || saved.delivery_address || '';
  state.termsAccepted = !!fields['terms-check'];
  goStep(4);
  document.getElementById('link-ready').classList.add('visible');
  document.getElementById('pay-buttons').style.display = 'none';
  const title = document.querySelector('#link-ready .link-ready-title');
  if (title) title.textContent = 'Your booking is saved — resume secure checkout';
  setTimeout(checkStep3, 50);
  return true;
}

// ── INIT ─────────────────────────────────────────────────────────────────────
'''
if s.count(anchor)!=1: sys.exit('ANCHOR ERROR init')
s=s.replace(anchor,restore,1); print('  ok: restore checkout after Stripe back/cancel')

# Modify Promise init to restore draft or URL/default
old='''Promise.all([loadPricing(), loadSettings()]).then(() => {
  // Pre-fill from URL params (?location=Isle+of+Palms&date=2026-06-15&days=5)
  (function() {
'''
new='''Promise.all([loadPricing(), loadSettings()]).then(() => {
  const query = new URLSearchParams(window.location.search);
  const restored = query.get('booking') !== 'success' && restoreCheckoutDraft();
  // Pre-fill from URL params (?location=Isle+of+Palms&date=2026-06-15&days=5)
  if (!restored) (function() {
'''
if s.count(old)!=1: sys.exit('ANCHOR ERROR promise init')
s=s.replace(old,new,1); print('  ok: restore saved checkout before normal initialization')

rep('''if (urlParams.get('booking') === 'success') {
  document.querySelector('.main').innerHTML = `
''','''if (urlParams.get('booking') === 'success') {
  clearBookingDraft();
  document.querySelector('.main').innerHTML = `
''','clear draft after payment success')

bak=P.with_suffix('.html.bak'); shutil.copy2(P,bak); P.write_text(s)
print('DONE: patched index.html')
