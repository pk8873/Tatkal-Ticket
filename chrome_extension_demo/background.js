chrome.runtime.onInstalled.addListener(() => {
  console.log("Railway Booking Assistant demo installed.");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "OPEN_DEMO") return;

  // Open the actual form page, not the directory listing.
  chrome.tabs.create({ url: "http://localhost:8000/demo/" })
    .then(() => sendResponse({ ok: true }))
    .catch((error) => sendResponse({ ok: false, error: String(error) }));

  return true;
});
