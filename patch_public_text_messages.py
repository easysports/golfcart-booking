#!/usr/bin/env python3
from pathlib import Path
import shutil, sys
P=Path('index.html')
if not P.exists(): sys.exit('ERROR: index.html not found')
s=P.read_text(); MARK='[text-messages-public-v1]'
if MARK in s: print('SKIP: public text/messages patch already applied'); sys.exit(0)

def rep(old,new,label):
 global s
 c=s.count(old)
 if c!=1: sys.exit(f'ANCHOR ERROR [{label}]: expected 1, found {c}')
 s=s.replace(old,new,1); print('  ok:',label)

pairs=[
("<h1>The Charleston Area's #1 LSV Rental 🛺</h1>","<h1 id=\"content-hero-title\">The Charleston Area's #1 LSV Rental 🛺</h1>","hero title"),
("<p>Street-legal luxury golf carts delivered directly to your door. Book in minutes.</p>","<p id=\"content-hero-subtitle\">Street-legal luxury golf carts delivered directly to your door. Book in minutes.</p>","hero subtitle"),
('''    <div class="hero-pill">🚚 Delivery to your Door</div>\n    <div class="hero-pill">🗝 Extension Cord Included</div>\n    <div class="hero-pill">📱 SMS Updates</div>\n    <div class="hero-pill">✅ Instant Confirmation</div>''','''    <div class="hero-pill" id="content-hero-pill-delivery">🚚 Delivery to your Door</div>\n    <div class="hero-pill" id="content-hero-pill-extension">🗝 Extension Cord Included</div>\n    <div class="hero-pill" id="content-hero-pill-sms">📱 SMS Updates</div>\n    <div class="hero-pill" id="content-hero-pill-confirmation">✅ Instant Confirmation</div>''','hero badges'),
('''      <div class="card-title">Choose your cart</div>\n      <div class="card-sub">Luxury LSV rentals delivered to your door across the Charleston area.</div>''','''      <div class="card-title" id="content-choose-cart-title">Choose your cart</div>\n      <div class="card-sub" id="content-choose-cart-subtitle">Luxury LSV rentals delivered to your door across the Charleston area.</div>''','cart selection copy'),
('''        <strong>Isle of Palms:</strong> rentals currently exclude Wild Dunes.''','''        <strong id="content-iop-notice-title">Isle of Palms:</strong> <span id="content-iop-notice-body">rentals currently exclude Wild Dunes.</span>''','IOP notice copy'),
('''          <div class="cart-name">4-Passenger</div>\n          <div class="cart-desc">Perfect for couples or small families</div>''','''          <div class="cart-name" id="content-cart-4-name">4-Passenger</div>\n          <div class="cart-desc" id="content-cart-4-description">Perfect for couples or small families</div>''','4-seat copy'),
('''          <div class="cart-name">6-Passenger</div>\n          <div class="cart-desc">Ideal for larger groups & families</div>''','''          <div class="cart-name" id="content-cart-6-name">6-Passenger</div>\n          <div class="cart-desc" id="content-cart-6-description">Ideal for larger groups & families</div>''','6-seat copy'),
('''      <div class="card-title">Pick your dates</div>''','''      <div class="card-title" id="content-dates-title">Pick your dates</div>''','dates title'),
('''      <div class="card-sub">Carts are delivered at 4:00 PM on your arrival day and picked up by 10:00 AM on checkout day.</div>''','''      <div class="card-sub" id="content-dates-subtitle">Carts are delivered at 4:00 PM on your arrival day and picked up by 10:00 AM on checkout day.</div>''','dates subtitle'),
('''      <div class="card-title">Delivery details</div>\n      <div class="card-sub">We deliver right to your door by 4:00 PM. We'll do our best to accommodate early arrivals, but no guarantees.</div>''','''      <div class="card-title" id="content-delivery-title">Delivery details</div>\n      <div class="card-sub" id="content-delivery-subtitle">We deliver right to your door by 4:00 PM. We'll do our best to accommodate early arrivals, but no guarantees.</div>''','delivery copy'),
('''          <strong style="color:var(--text);">Seabrook delivery rules</strong><br>\n          Enter the full delivery address. We automatically recognize the neighborhood, including close spellings.<br>\n          <strong>Gas cart required:</strong> Beach Club, Chateau By The Green, Creekwatch, Dunecrest, Duneloft, Live Oak, Marsh Walk, Ocean Winds, Shelter Cove, St. Christopher Oaks and Treeloft.<br>\n          <strong>No LSV rentals:</strong> Atrium Villas, Bay Point, Bohicket Marina Village, Golf Shore, Heron Point, High Hammock, Pelican Watch, Racquet Club and Wedgewood.<br>\n          <strong>Sealoft Villas:</strong> electric or gas is allowed; electric carts must charge in the driveway, never under the house. We do not provide an extension cord and recommend gas.''','''          <strong style="color:var(--text);" id="content-seabrook-note-title">Seabrook delivery rules</strong><br>\n          <span id="content-seabrook-note-intro">Enter the full delivery address. We automatically recognize the neighborhood, including close spellings.</span><br>\n          <strong>Gas cart required:</strong> <span id="content-seabrook-gas-only">Beach Club, Chateau By The Green, Creekwatch, Dunecrest, Duneloft, Live Oak, Marsh Walk, Ocean Winds, Shelter Cove, St. Christopher Oaks and Treeloft.</span><br>\n          <strong>No LSV rentals:</strong> <span id="content-seabrook-no-rentals">Atrium Villas, Bay Point, Bohicket Marina Village, Golf Shore, Heron Point, High Hammock, Pelican Watch, Racquet Club and Wedgewood.</span><br>\n          <span id="content-seabrook-sealoft"><strong>Sealoft Villas:</strong> electric or gas is allowed; electric carts must charge in the driveway, never under the house. We do not provide an extension cord and recommend gas.</span>''','Seabrook note copy'),
('''          <div class="card-title">Your info</div>\n          <div class="card-sub">We'll send your confirmation and cart access code to these details.</div>''','''          <div class="card-title" id="content-checkout-title">Your info</div>\n          <div class="card-sub" id="content-checkout-subtitle">We'll send your confirmation and cart access code to these details.</div>''','checkout copy'),
]
for old,new,label in pairs: rep(old,new,label)

anchor='''// ── PRICING — loaded dynamically from API ─────────────────────────────────────\n'''
block=r'''// [text-messages-public-v1]
let publishedContent = null;
function setContentText(id, value) {
  const el = document.getElementById(id);
  if (el && value !== undefined && value !== null) el.textContent = String(value);
}
function applyPublishedContent(content) {
  const c = content?.public_booking || {};
  const map = {
    'content-hero-title':'hero_title', 'content-hero-subtitle':'hero_subtitle',
    'content-hero-pill-delivery':'hero_pill_delivery', 'content-hero-pill-extension':'hero_pill_extension',
    'content-hero-pill-sms':'hero_pill_sms', 'content-hero-pill-confirmation':'hero_pill_confirmation',
    'content-choose-cart-title':'choose_cart_title', 'content-choose-cart-subtitle':'choose_cart_subtitle',
    'content-iop-notice-title':'iop_notice_title', 'content-iop-notice-body':'iop_notice_body',
    'content-cart-4-name':'cart_4_name', 'content-cart-4-description':'cart_4_description',
    'content-cart-6-name':'cart_6_name', 'content-cart-6-description':'cart_6_description',
    'content-dates-title':'dates_title', 'content-dates-subtitle':'dates_subtitle',
    'content-delivery-title':'delivery_title', 'content-delivery-subtitle':'delivery_subtitle',
    'content-seabrook-note-title':'seabrook_note_title', 'content-seabrook-note-intro':'seabrook_note_intro',
    'content-seabrook-gas-only':'seabrook_gas_only', 'content-seabrook-no-rentals':'seabrook_no_rentals',
    'content-seabrook-sealoft':'seabrook_sealoft', 'content-checkout-title':'checkout_title',
    'content-checkout-subtitle':'checkout_subtitle'
  };
  Object.entries(map).forEach(([id,key]) => setContentText(id, c[key]));
  ['next1','next2'].forEach(id => setContentText(id, c.continue_label));
  setContentText('next3', c.checkout_label);
  setContentText('open-link-btn', c.payment_label);
}
async function loadPublishedContent() {
  try {
    const r = await fetch(`${API}/content/public?ts=${Date.now()}`, { cache:'no-store' });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || 'Unable to load published text');
    publishedContent = j.content || {};
    applyPublishedContent(publishedContent);
  } catch (e) { console.warn('Published text settings unavailable; using page defaults.', e); }
}

'''
rep(anchor,block+anchor,'add public content loader')
rep('''Promise.all([loadPricing(), loadSettings()]).then(() => {''','''Promise.all([loadPricing(), loadSettings(), loadPublishedContent()]).then(() => {''','load published text on startup')

shutil.copy2(P,P.with_suffix('.html.bak')); P.write_text(s)
print('DONE: patched index.html')
