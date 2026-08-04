import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
const librarySource = fs.readFileSync(new URL("./checkoutStateIntegrity39E5171.js", import.meta.url), "utf8");

const context = { window: {} };
vm.createContext(context);
vm.runInContext(librarySource, context);
const integrity = context.window.ScheduleFleetCheckoutStateIntegrity39E5171;

assert.equal(integrity.VERSION, "3.9E.5.17.1");
assert.equal(integrity.normalizeAddress("  123   Easy ST "), "123 easy st");

const fourSeat = {
  cart_type: "4seat",
  resolved_cart_type: "4seat",
  quantity: 1,
  start_date: "2026-09-09",
  duration_days: 4,
  zone: "Seabrook Island",
  delivery_address: "123 Easy St",
  location_acknowledged: false,
  base_price: 349,
  delivery_fee: 99.99,
};
const sixSeat = { ...fourSeat, cart_type: "6seat", resolved_cart_type: "6seat", base_price: 439 };

const fourSelection = integrity.selectionFingerprint(fourSeat);
const sixSelection = integrity.selectionFingerprint(sixSeat);
assert.notEqual(fourSelection, sixSelection, "4-seat → 6-seat must invalidate availability and checkout state");
assert.equal(fourSelection, integrity.selectionFingerprint({ ...sixSeat, ...fourSeat }), "returning to the exact 4-seat selection is deterministic");
assert.notEqual(fourSelection, integrity.selectionFingerprint({ ...fourSeat, quantity: 2 }));
assert.notEqual(fourSelection, integrity.selectionFingerprint({ ...fourSeat, start_date: "2026-09-10" }));
assert.notEqual(fourSelection, integrity.selectionFingerprint({ ...fourSeat, duration_days: 5 }));
assert.notEqual(fourSelection, integrity.selectionFingerprint({ ...fourSeat, zone: "Edisto Beach" }));
assert.notEqual(fourSelection, integrity.selectionFingerprint({ ...fourSeat, delivery_address: "124 Easy St" }));
assert.notEqual(fourSelection, integrity.selectionFingerprint({ ...fourSeat, location_acknowledged: true }));
assert.notEqual(fourSelection, integrity.selectionFingerprint({ ...fourSeat, resolved_cart_type: "6seat_gas" }));

const fourQuote = integrity.quoteFingerprint(fourSeat, { taxRate: 0.09, surchargeRate: 0.03 });
assert.notEqual(fourQuote, integrity.quoteFingerprint({ ...fourSeat, base_price: 399 }, { taxRate: 0.09, surchargeRate: 0.03 }), "price changes must invalidate a saved Stripe checkout");
assert.notEqual(fourQuote, integrity.quoteFingerprint(fourSeat, { taxRate: 0.10, surchargeRate: 0.03 }));
assert.notEqual(fourQuote, integrity.quoteFingerprint({ ...fourSeat, delivery_fee: 79.99 }, { taxRate: 0.09, surchargeRate: 0.03 }));

assert.equal(integrity.availabilityCoversQuantity({ available: true, available_count: 4 }, 4), true);
assert.equal(integrity.availabilityCoversQuantity({ available: true, available_count: 3 }, 4), false);
assert.equal(integrity.availabilityCoversQuantity({ available: true }, 1), true);
assert.equal(integrity.availabilityCoversQuantity({ available: true }, 2), false, "multi-cart checkout fails closed without a count");
assert.equal(integrity.availabilityCoversQuantity({ available: false, available_count: 10 }, 1), false);

assert.match(html, /schedulefleet-public-version" content="3\.9E\.5\.17\.2"/);
assert.match(html, /checkoutStateIntegrity39E5171\.js/);
assert.match(html, /if \(n === 4\) checkStep4\(\)/, "checkout summary must refresh whenever Step 4 opens");
assert.match(html, /invalidateCheckoutState\('cart_type_changed'/);
assert.match(html, /invalidateCheckoutState\('quantity_changed'/);
assert.match(html, /invalidateCheckoutState\('start_date_changed'/);
assert.match(html, /invalidateCheckoutState\('duration_changed'/);
assert.match(html, /invalidateCheckoutState\('zone_changed'/);
assert.match(html, /invalidateCheckoutState\('delivery_address_changed'/);
assert.match(html, /invalidateCheckoutState\('location_acknowledgement_changed'/);
assert.match(html, /state\.availability_fingerprint = quantityAvailable \? currentSelectionFingerprint\(\) : null/);
assert.match(html, /quantity: String\(Number\(state\.quantity \|\| 1\)\)/, "availability calls must include requested quantity");
assert.match(html, /state\.checkout_summary_fingerprint = preflight\.quote_fingerprint/);
assert.match(html, /state\.checkout_fingerprint = preflight\.quote_fingerprint/);
assert.match(html, /refreshCurrentPriceFromPublishedPricing\(\)/, "Step 4 must re-read the current published price");
assert.match(html, /resetTermsAcceptance\(\)/, "material changes require policy re-acknowledgement");
assert.match(html, /restored_checkout_requires_revalidation/);
assert.doesNotMatch(html, /if \(n > 3 && \(!state\.zone \|\| !state\.delivery_address \|\| !state\.location_allowed\)\) return;/);

console.log("PASS checkout_state_integrity_39e5171 booking");
