// background.js

// This code runs in the background and can handle various tasks.

// Example: Listen for a message from a content script and respond.
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.message === "hello") {
      // Perform an action in response to the message.
      console.log("Received a 'hello' message from the content script.");

      // You can also send a response back to the content script if needed.
      sendResponse({ message: "Hi from background!" });
    }
  });


  chrome.contextMenus.removeAll(); // Remove existing context menu items

  chrome.contextMenus.create({
    title: "My Context Menu Item",
    id: "myContextMenu",
    contexts: ["selection"],
  });

  // Add a click event listener to the context menu item.
  chrome.contextMenus.onClicked.addListener(function (info, tab) {
    if (info.menuItemId === "myContextMenu") {
      // Handle the context menu item click event here.
      console.log("Context menu item clicked on text: " + info.selectionText);
    }
  });

  chrome.action.onClicked.addListener((tab) => {
    console.log("Clicked")
    chrome.windows.create({
      url: 'browserchatgpt.html',
      type: 'panel',
      width: 400,
      height: 600
    });
  });

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'GET_LOCATION_HOST') {
      const host = window.location.host;
      sendResponse({ host: host });
    }
  });