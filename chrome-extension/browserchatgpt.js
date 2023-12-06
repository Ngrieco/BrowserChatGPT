document.addEventListener('DOMContentLoaded', function () {
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");
  
    
    let current_url = ''
    function getActiveTabHostname() {
      chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        // tabs is an array of tab objects that match the query
        if (tabs.length > 0) {
          // Get the first tab (should be the active tab)
          const activeTab = tabs[0];
          const url = new URL(activeTab.url);
          const hostname = url.hostname;
  
          if (hostname !== current_url) {
            current_url = hostname;
            console.log("Changed webpage to ", hostname);
            sendURLToServer(current_url)
          } 
        }
      });
    }
  
    getActiveTabHostname()
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      getActiveTabHostname()
    });

      async function sendURLToServer(url) {
        const API_URL = "http://localhost:8750"; // Replace with your LLM app API URL
    
        setTimeout(() => {
            
            chatbox.scrollTo(0, chatbox.scrollHeight);
    
            // Determine the endpoint based on whether it's the first message
            const endpoint = "submit_url";
            
            // Send a request to the appropriate endpoint
            const requestOptions = {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ url: url }),
            };
    
            fetch(`${API_URL}/${endpoint}`, requestOptions)
                .then((res) => res.json())
                .then((data) => {
                    incomingChatLi.querySelector("p").textContent = data.response.trim();
                })
                .catch(() => {
                    incomingChatLi.querySelector("p").classList.add("error");
                    incomingChatLi.querySelector("p").textContent = "Oops! Something went wrong. Please try again.";
                })
                .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
            
            // Update the flag for subsequent messages
            isFirstMessage = false;
        }, 600);
    };
        
});