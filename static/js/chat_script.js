document.addEventListener('DOMContentLoaded', () => {
    const chatbox = document.getElementById('chatbox');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    // Function to add a message to the chatbox
    function displayMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');

        // --- MODIFICATION START ---
        if (sender === 'ai') {
            try {
                // Check if marked library is loaded
                if (typeof marked === 'undefined') {
                  console.error('Markdown library (marked.js) is not loaded! Displaying raw text.');
                  messageDiv.textContent = message; // Fallback to plain text
                } else {
                  // Use marked.parse() to convert Markdown to HTML
                  // Note: Consider using a sanitizer like DOMPurify in production for security
                  const htmlContent = marked.parse(message);
                  // Use innerHTML to render the generated HTML
                  messageDiv.innerHTML = htmlContent;
                }
            } catch (e) {
                console.error('Error parsing Markdown or setting innerHTML:', e);
                // Fallback to plain text display if parsing fails
                messageDiv.textContent = message;
            }
        } else {
            // For user messages, display as plain text (safer)
            messageDiv.textContent = message;
        }
        // --- MODIFICATION END ---

        chatbox.appendChild(messageDiv);
        // Scroll to the bottom
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    // Function to send message to backend and display response
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        // Display user message (using the updated displayMessage)
        displayMessage(messageText, 'user');
        userInput.value = ''; // Clear input field

        // Display thinking indicator
        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('message', 'ai-message', 'thinking'); // Added thinking class
        thinkingDiv.textContent = 'Thinking...'; // Keep this as plain text
        chatbox.appendChild(thinkingDiv);
        chatbox.scrollTop = chatbox.scrollHeight;

        try {
            // Send message to backend API
            const response = await fetch('/api/interact-llm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: messageText })
            });

            // Remove thinking indicator
            if (chatbox.contains(thinkingDiv)) {
                chatbox.removeChild(thinkingDiv);
            }

            if (!response.ok) {
                // Handle HTTP errors (like 500, 400)
                let errorMsg = `Sorry, an error occurred (Status: ${response.status}).`;
                try { // Try to get more specific error from JSON body
                    const errorData = await response.json();
                    errorMsg += ` ${errorData.error || 'Unknown server error.'}`;
                } catch (e) { /* Ignore if response body isn't JSON */ }
                displayMessage(errorMsg, 'ai'); // Display error using displayMessage (will be plain text)
                console.error('API Error Status:', response.status);
                return;
            }

            // Parse successful response
            const data = await response.json();

            // Display AI reply (using the updated displayMessage which handles Markdown)
            if (data && data.reply) {
                 displayMessage(data.reply, 'ai');
            } else {
                 displayMessage('Sorry, I received an unexpected response.', 'ai'); // Plain text error
                 console.warn("Received empty or invalid reply:", data);
            }

        } catch (error) {
             // Handle network errors or JSON parsing errors
             if (chatbox.contains(thinkingDiv)){
                  chatbox.removeChild(thinkingDiv);
             }
             console.error('Fetch/Network Error:', error);
             displayMessage('Sorry, there was an error communicating with the assistant.', 'ai'); // Plain text error
        }
    }

    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

});