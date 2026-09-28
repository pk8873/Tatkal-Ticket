chrome.runtime.onInstalled.addListener(() => {
  console.log("Railway Booking Assistant demo installed.");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "OPEN_DEMO") return;

  const demoUrl =
    message.target === "local"
      ? "http://localhost:8000/demo/"
      : "https://tatkal-ticket-bot.onrender.com/extension-demo";

  chrome.tabs.create({ url: demoUrl })
    .then(() => sendResponse({ ok: true, url: demoUrl }))
    .catch((error) => sendResponse({ ok: false, error: String(error) }));

  return true;
});
