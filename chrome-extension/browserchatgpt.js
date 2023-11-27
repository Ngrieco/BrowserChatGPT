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
    // const messageElement = document.createElement('div');
    //messageElement.classList.add(isUser ? 'user-message' : 'ai-message');
    if(isUser){
      message = "User: " + message
    } else {
      message = "AI: " + message
    }

    // Regular expression to match URLs in the message
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const messageWithLinks = message.replace(urlRegex, '<a href="$1">$1</a>');
    //console.log(messageWithLinks)

    messageElement = parseString(messageWithLinks)
    chatContainer.appendChild(messageElement);

    /*
    // messageElement.innerText = message;
    messageElement.innerText = messageWithLinks;

    // Create the anchor element
    const link = document.createElement('a');
    link.setAttribute('href', 'https://www.example.com');
    link.innerText = 'https://www.example.com';

    chatContainer.appendChild(messageElement);
    // chatContainer.appendChild(link);
    */
  };


  function parseString(inputString) {
    let messageElement = document.createElement('div');
    let linkArray = inputString.split(',').map(link => link.trim());
  
    linkArray.forEach(linkStr => {
      let tempDiv = document.createElement('div');
      tempDiv.innerHTML = linkStr;
  
      let nodes = tempDiv.childNodes;
  
      nodes.forEach(node => {
        if (node.nodeName === "#text") {
          messageElement.appendChild(document.createTextNode(node.nodeValue));
        } else if (node.nodeName === "A") {
          let link = document.createElement('a');
          link.setAttribute('href', node.getAttribute('href'));
          link.innerText = node.innerText;
          messageElement.appendChild(link);
        }
      });
  
      messageElement.appendChild(document.createTextNode(', ')); // Add a comma and space between links
    });
  
    // Remove the last comma and space if added
    if (messageElement.lastChild) {
      messageElement.removeChild(messageElement.lastChild);
    }
  
    return messageElement;
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









