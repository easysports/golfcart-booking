import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
const librarySource = fs.readFileSync(new URL("./checkoutStateIntegrity39E5171.js", import.meta.url), "utf8");
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]);
const mainSource = scripts.at(-1).split("// ── INIT")[0];

class ClassList {
  constructor() { this.values = new Set(); }
  add(...values) { values.forEach(value => this.values.add(value)); }
  remove(...values) { values.forEach(value => this.values.delete(value)); }
  toggle(value, force) {
    if (force === true) { this.values.add(value); return true; }
    if (force === false) { this.values.delete(value); return false; }
    if (this.values.has(value)) { this.values.delete(value); return false; }
    this.values.add(value); return true;
  }
  contains(value) { return this.values.has(value); }
}

function element(overrides = {}) {
  return {
    value: "",
    checked: false,
    disabled: false,
    textContent: "",
    innerHTML: "",
    src: "",
    type: "text",
    style: {},
    className: "",
    classList: new ClassList(),
    ...overrides,
  };
}

const ids = new Map();
const ensure = (id, overrides = {}) => {
  if (!ids.has(id)) ids.set(id, element(overrides));
  return ids.get(id);
};
[
  "btn4","btn6","next1","next2","next3","qty-selector","cart-photo-strip","cart-strip-img","cart-strip-label","cart-strip-qty",
  "date-input","dur-select","avail-bar","price-preview","location-availability","location-ack-input","location-rule","location-ack",
  "fname","lname","email","phone","notes","arrival-input","addr-input","sms-opt","terms-check","pay-btn","link-ready","pay-buttons",
  "order-empty","order-lines","ol-cart","ol-base","ol-zone","ol-del","ol-surcharge","ol-tax","ol-total","ol-dates",
].forEach(id => ensure(id));
for (let i = 1; i <= 4; i += 1) {
  ensure(`page${i}`); ensure(`sc${i}`); ensure(`sl${i}`); if (i < 4) ensure(`line${i}`);
}
ensure("date-input").value = "";
ensure("pay-buttons").style.display = "";

const document = {
  getElementById(id) { return ids.get(id) || null; },
  querySelector() { return null; },
  querySelectorAll() { return []; },
  createElement() { return element(); },
};
const sessionStore = new Map();
const sessionStorage = {
  getItem(key) { return sessionStore.get(key) ?? null; },
  setItem(key, value) { sessionStore.set(key, String(value)); },
  removeItem(key) { sessionStore.delete(key); },
};
const windowObject = { scrollTo() {}, location: { origin:"https://book.test", pathname:"/" } };
const context = vm.createContext({
  window: windowObject,
  document,
  sessionStorage,
  console,
  setTimeout,
  clearTimeout,
  URLSearchParams,
  Date,
  Math,
  Number,
  String,
  Object,
  Array,
  JSON,
  alert() {},
  fetch: async () => { throw new Error("fetch should not run in runtime unit test"); },
});
vm.runInContext(librarySource, context);
vm.runInContext(mainSource, context);

vm.runInContext(`
  pricingData = {
    seasons:[{id:'post',name:'Post-August 2026',start_date:'2026-08-09',end_date:null}],
    cartTypes:[
      {id:CART_TYPE_IDS['4seat'],key:'4seat'},
      {id:CART_TYPE_IDS['6seat'],key:'6seat'}
    ],
    durations:[
      {season_id:'post',cart_type_id:CART_TYPE_IDS['4seat'],days:4,price:349,enabled:true},
      {season_id:'post',cart_type_id:CART_TYPE_IDS['6seat'],days:4,price:439,enabled:true}
    ]
  };
  taxRate = 0.09;
  surchargeRate = 0.03;
`, context);

// An existing checkout must be destroyed by a material cart-type change.
vm.runInContext(`
  state.cart_type='4seat';
  state.resolved_cart_type='4seat';
  state.checkoutUrl='https://stripe.test/old';
  state.checkout_fingerprint='old';
  state.termsAccepted=true;
  document.getElementById('terms-check').checked=true;
  selectCart('6seat');
`, context);
assert.equal(vm.runInContext("state.checkoutUrl", context), null);
assert.equal(vm.runInContext("state.termsAccepted", context), false);
assert.equal(ensure("terms-check").checked, false);
assert.equal(vm.runInContext("state.resolved_cart_type", context), null);

function renderSummary(cartType, price) {
  vm.runInContext(`
    state.cart_type=${JSON.stringify(cartType)};
    state.resolved_cart_type=${JSON.stringify(cartType)};
    state.quantity=1;
    state.start_date='2026-09-09';
    state.duration_days=4;
    state.base_price=${price};
    state.season='Post-August 2026';
    state.zone='Seabrook Island';
    state.delivery_fee=99.99;
    state.delivery_address='123 Easy St';
    state.location_acknowledged=false;
    state.location_allowed=true;
    state.avail={available:true,available_count:16};
    state.availability_fingerprint=currentSelectionFingerprint();
    goStep(4);
  `, context);
  return { label: ensure("ol-cart").textContent, total: ensure("ol-total").textContent };
}

const four = renderSummary("4seat", 349);
assert.match(four.label, /4-day 4-Passenger/);
const six = renderSummary("6seat", 349); // intentionally stale input; Step 4 must re-read 439.
assert.match(six.label, /4-day 6-Passenger/);
assert.notEqual(six.total, four.total);
assert.equal(vm.runInContext("state.base_price", context), 439);
const fourAgain = renderSummary("4seat", 439); // intentionally stale input; Step 4 must re-read 349.
assert.match(fourAgain.label, /4-day 4-Passenger/);
assert.equal(fourAgain.total, four.total);
assert.equal(vm.runInContext("state.base_price", context), 349);

const diagnostics = windowObject.__SCHEDULEFLEET_CHECKOUT_STATE_DIAGNOSTICS__;
assert.equal(diagnostics.version, "3.9E.5.17.1");
assert.equal(diagnostics.state, "ready");
assert.equal(diagnostics.cart_type, "4seat");

console.log("PASS checkout_state_runtime_39e5171 booking");
