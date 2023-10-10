document.addEventListener('DOMContentLoaded', function () {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
  
    // Event listener for sending messages
    sendButton.addEventListener('click', function () {
      const userMessage = userInput.value;
      // You can implement code to send userMessage to ChatGPT here
      // Append the response to chatContainer
      appendMessage(userMessage, true);
      // Clear the user input field
      userInput.value = '';
    });
  
    // Function to append messages to the chatContainer
    function appendMessage(message, isUser) {
      const messageElement = document.createElement('div');
      messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
      messageElement.innerText = message;
      chatContainer.appendChild(messageElement);
    }
  });
  