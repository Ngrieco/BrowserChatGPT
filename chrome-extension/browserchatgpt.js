document.addEventListener('DOMContentLoaded', function () {
  // DOM element references
  const closeBtn = document.querySelector(".close-btn");
  const chatbox = document.querySelector(".chatbox");
  const chatInput = document.querySelector(".chat-input textarea");
  const sendChatBtn = document.querySelector(".chat-input span");

  // Variable to track the current URL
  let current_url = '';

  // Function to get the active tab's hostname
  function getActiveTabHostname() {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      if (tabs.length > 0) {
        const activeTab = tabs[0];
        const url = new URL(activeTab.url);
        const hostname = url.hostname;

        // Check if the hostname has changed
        if (hostname !== current_url) {
          current_url = hostname;
          console.log("Changed webpage to ", hostname);

          // Call the function to send the URL to the server
          sendURLToServer(current_url);
        }
      }
    });
  }

  // Initial call to get the active tab's hostname
  getActiveTabHostname();

  // Listen for tab updates to track changes in the active tab
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    getActiveTabHostname();
  });

  // Function to send the current URL to the server
  async function sendURLToServer(url) {
    const API_URL = "http://localhost:8750"; // Replace with your LLM app API URL

    // Delay the execution to simulate user typing
    setTimeout(() => {
      // Scroll to the bottom of the chatbox
      chatbox.scrollTo(0, chatbox.scrollHeight);

      // Define the API endpoint for submitting URLs
      const endpoint = "submit_url";

      // Prepare the request options
      const requestOptions = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url }),
      };

      // Make a fetch request to the server
      fetch(`${API_URL}/${endpoint}`, requestOptions)
        .then((res) => res.json())
        .then((data) => {
          // Update the chatbox with the server response
          incomingChatLi.querySelector("p").textContent = data.response.trim();
        })
        .catch(() => {
          // Handle errors if the request fails
          incomingChatLi.querySelector("p").classList.add("error");
          incomingChatLi.querySelector("p").textContent = "Oops! Something went wrong. Please try again.";
        })
        .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
    }, 600);
  }
});
