import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
const moduleSource = fs.readFileSync(new URL("./buildIdentity39E5172.js", import.meta.url), "utf8");

assert.match(html, /schedulefleet-public-version" content="3\.9E\.5\.17\.3"/);
assert.match(html, /Booking v3\.9E\.5\.17\.3/);
assert.match(html, /buildIdentity39E5172\.js/);
assert.match(html, /const PUBLIC_BOOKING_VERSION = '3\.9E\.5\.17\.3'/);
assert.match(html, /ScheduleFleetBuildIdentity39E5172\?\.load\(\{ apiBase: API \}\)/);
assert.match(moduleSource, /const VERSION = "3\.9E\.5\.17\.3"/);
assert.match(moduleSource, /__SCHEDULEFLEET_BUILD_IDENTITY__/);
assert.match(moduleSource, /\/version\?ts=/);

const elements = new Map();
const context = {
  window: {},
  document: { getElementById(id) { if (!elements.has(id)) elements.set(id, { textContent: "", hidden: true }); return elements.get(id); } },
  fetch: async () => ({ ok: true, json: async () => ({ version: "v1.9.15 · abc1234", built: "08/04/26 12:30 PM auto-import" }) }),
  Date,
  setTimeout,
  clearTimeout,
  console,
};
vm.createContext(context);
vm.runInContext(moduleSource, context);
assert.equal(context.window.ScheduleFleetBuildIdentity39E5172.VERSION, "3.9E.5.17.3");
const identity = await context.window.ScheduleFleetBuildIdentity39E5172.load({ apiBase: "https://api.example.com" });
assert.equal(identity.api_ok, true);
assert.equal(identity.api_version, "v1.9.15 · abc1234");
assert.equal(context.window.__SCHEDULEFLEET_BUILD_IDENTITY__.version, "3.9E.5.17.3");
context.window.ScheduleFleetBuildIdentity39E5172.toggle();
assert.equal(elements.get("schedulefleet-build-details").hidden, false);

console.log("PASS build_identity_39e5172 booking");
