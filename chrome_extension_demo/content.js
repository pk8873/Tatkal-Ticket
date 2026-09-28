function setField(selector, value) {
  const element = document.querySelector(selector);
  if (!element || value === undefined || value === null) return false;

  element.focus();
  element.value = String(value);
  element.dispatchEvent(new Event("input", { bubbles: true }));
  element.dispatchEvent(new Event("change", { bubbles: true }));
  return true;
}

function fillDemoForm(data) {
  const results = {
    source: setField("#source", data.source),
    destination: setField("#destination", data.destination),
    travelDate: setField("#travelDate", data.travelDate),
    train: setField("#train", data.train),
    boarding: setField("#boarding", data.boarding)
  };

  const quota = document.querySelector("#quota");
  if (quota) {
    results.quota = data.quota
      ? setField("#quota", data.quota)
      : true;
  } else {
    results.quota = false;
  }

  return results;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "FILL_DEMO_FORM") return;

  try {
    const results = fillDemoForm(message.data || {});
    const filledCount = Object.values(results).filter(Boolean).length;

    sendResponse({
      ok: filledCount > 0,
      results,
      filledCount
    });
  } catch (error) {
    sendResponse({
      ok: false,
      error: String(error)
    });
  }
});
