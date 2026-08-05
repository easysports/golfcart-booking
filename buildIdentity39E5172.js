(() => {
  const VERSION = "3.9E.5.17.3";

  const text = value => String(value ?? "").trim();
  const setText = (id, value) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  };

  async function load({ apiBase }) {
    const identity = {
      version: VERSION,
      public_booking: `Booking v${VERSION}`,
      api_version: null,
      api_built: null,
      api_ok: false,
      checked_at: new Date().toISOString(),
    };
    setText("schedulefleet-public-version-label", `Booking v${VERSION}`);
    try {
      const response = await fetch(`${String(apiBase || "").replace(/\/$/, "")}/version?ts=${Date.now()}`, { cache: "no-store" });
      const payload = await response.json();
      identity.api_ok = response.ok;
      identity.api_version = text(payload?.version) || null;
      identity.api_built = text(payload?.built) || null;
      setText("schedulefleet-build-api", identity.api_version ? `API ${identity.api_version}` : "API version unavailable");
      setText("schedulefleet-build-time", identity.api_built || "Build time unavailable");
    } catch (error) {
      identity.error = error?.message || String(error);
      setText("schedulefleet-build-api", "API version unavailable");
      setText("schedulefleet-build-time", "Try refreshing this page");
    }
    window.__SCHEDULEFLEET_BUILD_IDENTITY__ = identity;
    return identity;
  }

  function toggle() {
    const details = document.getElementById("schedulefleet-build-details");
    if (!details) return;
    details.hidden = !details.hidden;
  }

  window.ScheduleFleetBuildIdentity39E5172 = { VERSION, load, toggle };
})();
