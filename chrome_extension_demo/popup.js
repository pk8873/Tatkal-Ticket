const ids = ["source", "destination", "travelDate", "train", "boarding", "quota"];

function getData() {
  return Object.fromEntries(ids.map(id => [id, document.getElementById(id).value]));
}

function setStatus(message) {
  document.getElementById("status").textContent = message;
}

async function loadSaved() {
  const saved = await chrome.storage.local.get("bookingData");
  const data = saved.bookingData || {};

  for (const id of ids) {
    if (data[id] !== undefined) {
      document.getElementById(id).value = data[id];
    }
  }
}

document.getElementById("save").addEventListener("click", async () => {
  await chrome.storage.local.set({ bookingData: getData() });
  setStatus("Saved locally in this browser.");
});

document.getElementById("open").addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "OPEN_DEMO" }, response => {
    setStatus(response?.ok ? "Demo opened." : "Could not open demo.");
  });
});

document.getElementById("fill").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!tab?.url?.startsWith("http://localhost/") &&
      !tab?.url?.startsWith("http://127.0.0.1/")) {
    setStatus("Open the local demo page first.");
    return;
  }

  chrome.tabs.sendMessage(
    tab.id,
    { type: "FILL_DEMO_FORM", data: getData() },
    response => {
      if (chrome.runtime.lastError) {
        setStatus("Refresh the demo page, then try again.");
        return;
      }
      setStatus(response?.ok ? "Demo form filled." : "Fill failed.");
    }
  );
});

loadSaved();
