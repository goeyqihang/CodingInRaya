document.addEventListener('DOMContentLoaded', () => {
    const chatbox = document.getElementById('chatbox');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    // const newChatButton = document.getElementById('new-chat-button'); // REMOVED or commented out

    // --- NEW: Client-side chat history array ---
    let chatHistory = [];
    const MAX_HISTORY_TURNS = 10; // Max conversation turns (1 turn = user + assistant) to keep

    // Function to add a message to the chatbox (Handles Markdown for AI)
    function displayMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');

        // Use a nested div for easier styling and selection if needed
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');

        if (sender === 'ai' && window.marked) {
            try {
                messageContent.innerHTML = marked.parse(message, { gfm: true, breaks: true });
            } catch (e) {
                console.error('Markdown parsing error:', e);
                messageContent.textContent = message; // Fallback
            }
        } else {
            messageContent.textContent = message; // User or system messages
        }
        messageDiv.appendChild(messageContent);
        chatbox.appendChild(messageDiv);
        chatbox.scrollTop = chatbox.scrollHeight; // Scroll to bottom
    }

    // --- NEW: Function to add message object to history and limit size ---
    function addMessageToHistory(role, content) {
        chatHistory.push({ role: role, content: content });
        // Limit history length
        if (chatHistory.length > MAX_HISTORY_TURNS * 2) {
            // Keep only the last MAX_HISTORY_TURNS * 2 messages
            // Typically slice from the second element if System Prompt isn't in history,
            // but here we manage the full history including initial AI message.
            chatHistory = chatHistory.slice(-(MAX_HISTORY_TURNS * 2));
            console.log(`Chat history limited to ${chatHistory.length} messages.`);
        }
    }


    // Function to send message to backend and display response
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        // Display user message visually
        displayMessage(messageText, 'user');

        // --- NEW: Add user message to client-side history ---
        addMessageToHistory('user', messageText);

        userInput.value = ''; // Clear input field

        // Display thinking indicator
        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('message', 'ai-message', 'thinking');
        thinkingDiv.innerHTML = '<div class="message-content">Thinking...</div>'; // Use innerHTML for consistency
        chatbox.appendChild(thinkingDiv);
        chatbox.scrollTop = chatbox.scrollHeight;

        try {
            // --- MODIFIED: Send history in the request body ---
            const response = await fetch('/api/interact-llm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // Send the current state of chatHistory
                body: JSON.stringify({ history: chatHistory })
            });

            // Remove thinking indicator
            if (chatbox.contains(thinkingDiv)) {
                chatbox.removeChild(thinkingDiv);
            }

            // Inside the try block, after fetch is successful:

            if (!response.ok) {
                // ... (error handling as before, maybe remove user message from history) ...
                if (chatHistory.length > 0 && chatHistory[chatHistory.length - 1].role === 'user') { chatHistory.pop(); }
                return;
            }

            const data = await response.json();

            // --- MODIFIED: Handle multiple replies ---
            if (data && data.replies && Array.isArray(data.replies) && data.replies.length > 0) {
                for (let i = 0; i < data.replies.length; i++) {
                    const replyText = data.replies[i];

                    // Optional: Add delay before showing the second, third, etc., reply
                    if (i > 0) {
                        // Add a delay (e.g., 750 milliseconds)
                        await new Promise(resolve => setTimeout(resolve, 750));

                        // Optional: Add/remove a temporary "typing" indicator during delay
                        const typingIndicator = document.createElement('div');
                        typingIndicator.classList.add('message', 'ai-message', 'thinking');
                        typingIndicator.innerHTML = '<div class="message-content">...</div>';
                        chatbox.appendChild(typingIndicator);
                        chatbox.scrollTop = chatbox.scrollHeight;
                        await new Promise(resolve => setTimeout(resolve, 600)); // Shorter delay for typing dots
                        if (chatbox.contains(typingIndicator)) {
                            chatbox.removeChild(typingIndicator);
                        }
                    }

                    // Display the current reply visually
                    displayMessage(replyText, 'ai');
                    // Add the current AI reply to client-side history
                    addMessageToHistory('assistant', replyText);
                }
            } else {
                // Handle cases where response is empty or invalid
                displayMessage('Sorry, I received an unexpected response format.', 'ai');
                console.warn("Received empty or invalid replies array:", data);
                // Remove user message from history as the response was bad
                if (chatHistory.length > 0 && chatHistory[chatHistory.length - 1].role === 'user') { chatHistory.pop(); }
            }
            // Log current history state (optional for debugging)
            console.log("Current client history:", chatHistory);
            // --- END OF MODIFIED REPLY HANDLING ---

        } catch (error) {
            // ... (network/fetch error handling as before, maybe remove user message from history) ...
            if (chatbox.contains(thinkingDiv)) { chatbox.removeChild(thinkingDiv); } // Ensure thinking removed
            console.error('Fetch/Network Error:', error);
            displayMessage('Sorry, there was an error communicating with the assistant.', 'ai');
            if (chatHistory.length > 0 && chatHistory[chatHistory.length - 1].role === 'user') { chatHistory.pop(); }
        }
    } // End of sendMessage function

    // Event Listeners for sending
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    // --- REMOVED: Event listener for the "New Chat" button ---
    // newChatButton.addEventListener('click', async () => { ... }); // REMOVED

    // --- Add Initial Welcome Message ---
    const initialMessage = "Hello! I'm the MEX Assistant. How can I help you today?";
    displayMessage(initialMessage, 'ai');
    // --- NEW: Add initial message to history as well ---
    // We start history with the AI's first message
    addMessageToHistory('assistant', initialMessage);

});