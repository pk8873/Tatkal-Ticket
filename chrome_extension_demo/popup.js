const ids = ["source", "destination", "travelDate", "train", "boarding", "quota"];

function getData() {
  return Object.fromEntries(
    ids.map(id => [id, document.getElementById(id).value])
  );
}

function setStatus(message) {
  document.getElementById("status").textContent = message;
}

function isSupportedPage(url) {
  if (!url) return false;

  return (
    url.startsWith("http://localhost:") ||
    url.startsWith("http://127.0.0.1:") ||
    url.startsWith("https://tatkal-ticket-bot.onrender.com/")
  );
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
  try {
    await chrome.storage.local.set({ bookingData: getData() });
    setStatus("Saved locally in this browser.");
  } catch (error) {
    setStatus("Save failed: " + error.message);
  }
});

document.getElementById("open").addEventListener("click", () => {
  setStatus("Opening demo...");

  chrome.runtime.sendMessage({ type: "OPEN_DEMO" }, response => {
    if (chrome.runtime.lastError) {
      setStatus("Extension service error. Reload the extension.");
      return;
    }

    setStatus(
      response?.ok
        ? "Demo opened. Now click Fill Current Demo Page."
        : "Could not open demo."
    );
  });
});

async function fillUsingScripting(tabId, data) {
  const results = await chrome.scripting.executeScript({
    target: { tabId },
    func: (formData) => {
      function setField(selector, value) {
        const element = document.querySelector(selector);
        if (!element || value === undefined || value === null) return false;

        element.focus();
        element.value = String(value);
        element.dispatchEvent(new Event("input", { bubbles: true }));
        element.dispatchEvent(new Event("change", { bubbles: true }));
        return true;
      }

      const result = {
        source: setField("#source", formData.source),
        destination: setField("#destination", formData.destination),
        travelDate: setField("#travelDate", formData.travelDate),
        train: setField("#train", formData.train),
        boarding: setField("#boarding", formData.boarding),
        quota: setField("#quota", formData.quota)
      };

      const filledCount = Object.values(result).filter(Boolean).length;
      return { ...result, filledCount };
    },
    args: [data]
  });

  return results?.[0]?.result;
}

document.getElementById("fill").addEventListener("click", async () => {
  setStatus("Checking current page...");

  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    });

    if (!tab?.id || !isSupportedPage(tab.url)) {
      setStatus(
        "Open localhost demo or the deployed /extension-demo page first."
      );
      return;
    }

    const data = getData();
    let result = null;

    try {
      result = await chrome.tabs.sendMessage(tab.id, {
        type: "FILL_DEMO_FORM",
        data
      });
    } catch (contentScriptError) {
      result = await fillUsingScripting(tab.id, data);
    }

    if (result?.filledCount > 0) {
      setStatus(
        "Demo form filled: " + result.filledCount + "/6 fields."
      );
    } else {
      setStatus(
        "No matching demo fields found. Open the demo page and refresh it."
      );
    }
  } catch (error) {
    console.error(error);
    setStatus("Fill failed: " + error.message);
  }
});

loadSaved().catch(error => {
  console.error(error);
  setStatus("Could not load saved data.");
});
