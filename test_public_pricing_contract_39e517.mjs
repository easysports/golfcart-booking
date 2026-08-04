import assert from "node:assert/strict";
import fs from "node:fs";

const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
assert.match(html, /schedulefleet-public-version" content="3\.9E\.5\.17"/);
assert.match(html, /const REQUIRED_PUBLIC_CART_KEYS = Object\.freeze\(\['4seat', '6seat'\]\)/);
assert.match(html, /const OPTIONAL_PUBLIC_CART_KEYS = Object\.freeze\(\['6seat_gas', '6seat_wild_dunes'\]\)/);
assert.match(html, /Their absence\n  \/\/ must never disable ordinary 4- and 6-passenger public checkout/);
assert.match(html, /for \(let attempt = 1; attempt <= 2; attempt \+= 1\)/);
assert.match(html, /window\.__SCHEDULEFLEET_PRICING_DIAGNOSTICS__/);
assert.doesNotMatch(html, /for \(const \[key,id\] of Object\.entries\(CART_TYPE_IDS\)\)/, "all cart types must not be unconditionally required");
console.log("PASS public_pricing_contract_39e517 booking");
