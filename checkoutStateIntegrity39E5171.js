(function attachScheduleFleetCheckoutIntegrity(global) {
  'use strict';

  const VERSION = '3.9E.5.17.1';

  function normalizeAddress(value) {
    return String(value || '')
      .trim()
      .replace(/\s+/g, ' ')
      .toLowerCase();
  }

  function positiveInteger(value, fallback = 1) {
    const parsed = Number.parseInt(value, 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
  }

  function nullablePositiveInteger(value) {
    const parsed = Number.parseInt(value, 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
  }

  function selectionSnapshot(state = {}) {
    return {
      cart_type: state.cart_type || null,
      resolved_cart_type: state.resolved_cart_type || state.cart_type || null,
      quantity: positiveInteger(state.quantity, 1),
      start_date: state.start_date || null,
      duration_days: nullablePositiveInteger(state.duration_days),
      zone: state.zone || null,
      delivery_address: normalizeAddress(state.delivery_address),
      location_acknowledged: !!state.location_acknowledged,
    };
  }

  function selectionFingerprint(state = {}) {
    return JSON.stringify(selectionSnapshot(state));
  }

  function quoteSnapshot(state = {}, rates = {}) {
    return {
      selection: selectionSnapshot(state),
      base_price: Number(state.base_price || 0),
      delivery_fee: Number(state.delivery_fee || 0),
      tax_rate: Number(rates.taxRate || 0),
      surcharge_rate: Number(rates.surchargeRate || 0),
    };
  }

  function quoteFingerprint(state = {}, rates = {}) {
    return JSON.stringify(quoteSnapshot(state, rates));
  }

  function availabilityCoversQuantity(availability, quantity) {
    if (!availability || availability.available !== true) return false;
    const requested = positiveInteger(quantity, 1);
    const availableCount = Number(availability.available_count);
    if (Number.isFinite(availableCount)) return availableCount >= requested;
    return requested === 1;
  }

  function fingerprintsMatch(left, right) {
    return typeof left === 'string' && left.length > 0 && left === right;
  }

  const api = Object.freeze({
    VERSION,
    normalizeAddress,
    selectionSnapshot,
    selectionFingerprint,
    quoteSnapshot,
    quoteFingerprint,
    availabilityCoversQuantity,
    fingerprintsMatch,
  });

  global.ScheduleFleetCheckoutStateIntegrity39E5171 = api;
})(typeof window !== 'undefined' ? window : globalThis);
