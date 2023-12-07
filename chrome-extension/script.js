// DOM element references
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

// Variable to store user's message
let userMessage = null;
// Replace with your LLM app API URL
const API_URL = "http://localhost:8750";
// Initial height of the input textarea
const inputInitHeight = chatInput.scrollHeight;

// Function to create a chat <li> element
const createChatLi = (message, className) => {
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", `${className}`);
  let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message;
  return chatLi;
};

// Function to generate a response from the server
const generateResponse = () => {
  const messageElement = document.createElement("p");

  // Define properties and message for the API request
  const requestOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: userMessage }),
  };

  // Send a POST request to the API, get response, and set the response as paragraph text
  fetch(`${API_URL}/submit_query`, requestOptions)
    .then((res) => res.json())
    .then((data) => {
      messageElement.textContent = data.response.trim();
      chatbox.appendChild(createChatLi(messageElement.textContent, "incoming"));
    })
    .catch(() => {
      messageElement.classList.add("error");
      messageElement.textContent = "Oops! Something went wrong. Please try again.";
      chatbox.appendChild(createChatLi(messageElement.textContent, "incoming"));
    })
    .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
};

// Flag to track the first message
let isFirstMessage = true;

// Function to handle user messages
const handleChat = () => {
  userMessage = chatInput.value.trim(); // Get user-entered message and remove extra whitespace
  if (!userMessage) return;

  // Clear the input textarea and set its height to default
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Append the user's message to the chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    // Display "Thinking..." message while waiting for the response
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);

    // Determine the endpoint based on whether it's the first message
    const endpoint = isFirstMessage ? "submit_url" : "submit_query";

    // Send a request to the appropriate endpoint
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(isFirstMessage ? { url: userMessage } : { query: userMessage }),
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

// Event listener for input changes to adjust the height of the input textarea
chatInput.addEventListener("input", () => {
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

// Event listener for Enter key press to handle the chat
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

// Event listener for clicking the send button to handle the chat
sendChatBtn.addEventListener("click", handleChat);
