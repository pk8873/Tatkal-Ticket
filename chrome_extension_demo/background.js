chrome.runtime.onInstalled.addListener(() => {
  console.log("Railway Booking Assistant demo installed.");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "OPEN_DEMO") return;

  chrome.tabs.create({ url: "http://localhost:8000/" })
    .then(() => sendResponse({ ok: true }))
    .catch((error) => sendResponse({ ok: false, error: String(error) }));

  return true;
});
