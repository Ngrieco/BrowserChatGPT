document.addEventListener('DOMContentLoaded', function () {
  const chatContainer = document.getElementById('chat-container');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-button');

  
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


  // Event listener for submitting user query on Enter key press
  userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
      submitUserQuery();
    }
  });


  function addMessageToGUI(message, isUser) {
    const messageElement = document.createElement('div');
    messageElement.classList.add(isUser ? 'user-message' : 'ai-message');
    if(isUser){
      message = "User: " + message
    } else {
      message = "AI: " + message
    }

    const messageWithLinks = parseStringIntoElements(message)
    chatContainer.appendChild(messageWithLinks);
  };


  function parseStringIntoElements(string) {
    const container = document.createElement('div');
    const segments = string.split(/(https?:\/\/[^\s,]+)/); 

    segments.forEach(segment => {
      if (segment.startsWith('http')) {
        const link = document.createElement('a');
        
        if (segment.endsWith('.')) {
          segment = segment.slice(0, -1); // Remove the last character (period)
        }

        link.href = segment.trim(); // Trim to remove any leading/trailing whitespace
        link.textContent = segment.trim();
        link.target = "_blank";
  
        container.appendChild(link); // Append link directly to the container
      } else {
        const span = document.createElement('span');
        span.textContent = segment;
  
        container.appendChild(span); // Append segment directly to the container
      }
    });

    return container;
  }


  // Function to handle sending querys
  async function submitUserQuery() {
    const userMessage = userInput.value.trim();
    
    if (userMessage !== '') {
      addMessageToGUI(userMessage, true);
      // You can implement code to send userMessage to ChatGPT here
      // Append the response to chatContainer
      userInput.value = '';

      // const aiMessage = "Ok, that sounds great.";
      aiMessage = await sendQueryToServer(userMessage)
      console.log("ai message ", aiMessage)
      addMessageToGUI(aiMessage, false);
    }
  };


  async function sendURLToServer(url) {
    const serverURL = "http://127.0.0.1:5000/api/url"; // Update this URL if needed
  
    const params = new URLSearchParams({ url });
    const response = await fetch(`${serverURL}?${params}`);
    
    if (response.ok) {
      const data = await response.json();
      const success = data.success;
      console.log(`URL Result: ${success}`);
    } else {
      console.error('Error: Failed to send URL.');
      console.error('Code:', response.status);
    }
  };
  

  async function sendQueryToServer(query) {
    const serverURL = 'http://127.0.0.1:5000/api/query'; // Update this URL if needed
  
    const params = new URLSearchParams({ query });
    const response = await fetch(`${serverURL}?${params}`);
    
    if (response.ok) {
      const data = await response.json();
      const responseData = data.response;
      console.log(`Query Result: ${data}`);
      console.log(`Query responseData: ${responseData}`);

      return responseData;
    } else {
      console.error('Error: Failed to get query result.');
      console.error('Code:', response.status);
      return null;
    }
  };

});









