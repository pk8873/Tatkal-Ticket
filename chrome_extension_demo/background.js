chrome.runtime.onInstalled.addListener(() => {
  console.log("Railway Booking Assistant demo installed.");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "OPEN_DEMO") return;

  const localDemo = "http://localhost:8000/demo/";
  const deployedDemo = "https://tatkal-ticket-bot.onrender.com/extension-demo";

  chrome.tabs.create({ url: localDemo })
    .then(() => sendResponse({ ok: true, url: localDemo }))
    .catch(() => {
      chrome.tabs.create({ url: deployedDemo })
        .then(() => sendResponse({ ok: true, url: deployedDemo }))
        .catch((error) => sendResponse({ ok: false, error: String(error) }));
    });

  return true;
});
