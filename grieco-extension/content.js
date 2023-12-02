// content.js

// This code runs whenever the extension is activated on a web page.

// You can add your JavaScript code here to interact with the web page.
// For example, you can manipulate the DOM, send data to the background script,
// or perform any other actions you need.

// Example: Change the background color of the page to red.
document.body.style.backgroundColor = 'red';

// You can also listen for events and respond to them.
// Example: Add a click event listener to a button with the ID "myButton."
const myButton = document.getElementById('myButton');
if (myButton) {
  myButton.addEventListener('click', function () {
    // Handle the button click event here.
    alert('Button clicked!');
  });
}
