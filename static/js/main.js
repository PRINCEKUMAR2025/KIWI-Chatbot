document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatContainer = document.getElementById('chatContainer');
    
    // Event listener for form submission
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input field
        userInput.value = '';
        
        // Show loading indicator
        const loadingId = showLoadingIndicator();
        
        // Send message to API
        sendMessageToAPI(message)
            .then(response => {
                // Remove loading indicator
                removeLoadingIndicator(loadingId);
                
                // Add bot response to chat
                addMessageToChat('bot', response.response);
                
                // Scroll to bottom of chat
                scrollToBottom();
            })
            .catch(error => {
                // Remove loading indicator
                removeLoadingIndicator(loadingId);
                
                // Add error message to chat
                addMessageToChat('error', 'Sorry, there was an error processing your request. Please try again.');
                console.error('Error:', error);
                
                // Scroll to bottom of chat
                scrollToBottom();
            });
    });
    
    // Function to add a message to the chat
    function addMessageToChat(type, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = type + '-message';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // If message contains a list (indicated by ->) format it
        if (message.includes('->')) {
            const formattedMessage = formatStructuredMessage(message);
            messageContent.innerHTML = formattedMessage;
        } else {
            messageContent.textContent = message;
        }
        
        messageDiv.appendChild(messageContent);
        chatContainer.appendChild(messageDiv);
        
        // Scroll to the new message
        scrollToBottom();
    }
    
    // Function to format structured messages
    function formatStructuredMessage(message) {
        // Split by newlines first
        const lines = message.split('\n');
        let formattedMessage = '';
        
        for (const line of lines) {
            // Check if line contains ->
            if (line.includes('->')) {
                const [label, value] = line.split('->');
                formattedMessage += `<strong>${label.trim()}</strong>: ${value.trim()}<br>`;
            } else {
                formattedMessage += line + '<br>';
            }
        }
        
        return formattedMessage;
    }
    
    // Function to show loading indicator
    function showLoadingIndicator() {
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'bot-message';
        
        const loadingContent = document.createElement('div');
        loadingContent.className = 'message-content loading';
        loadingContent.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        
        loadingDiv.appendChild(loadingContent);
        chatContainer.appendChild(loadingDiv);
        
        // Scroll to the loading indicator
        scrollToBottom();
        
        return loadingId;
    }
    
    // Function to remove loading indicator
    function removeLoadingIndicator(loadingId) {
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
    }
    
    // Function to send message to API
    function sendMessageToAPI(message) {
        return fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                // You could add user_id here if needed
                // user_id: 'some-user-id'
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        });
    }
    
    // Function to scroll to bottom of chat
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

// Function to add sample query to input field and focus
function addSampleQuery(query) {
    const userInput = document.getElementById('userInput');
    userInput.value = query;
    userInput.focus();
}