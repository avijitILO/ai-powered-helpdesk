const API_URL = 'http://localhost:8000/api';
let sessionId = generateSessionId();

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9);
}

// DOM elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const ticketList = document.getElementById('ticketList');

// Event listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Department buttons
document.querySelectorAll('.dept-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const dept = e.target.dataset.dept;
        messageInput.value = `I need help with ${dept} related issue`;
        messageInput.focus();
    });
});

// Send message function
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Display user message
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show loading indicator
    const loadingId = addLoadingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                user_id: 'demo_user'
            })
        });
        
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        // Display bot response
        addMessage(data.response, 'bot', {
            department: data.department,
            ticket_id: data.ticket_id,
            sources: data.sources
        });
        
        // Update ticket list if new ticket created
        if (data.ticket_id) {
            loadRecentTickets();
        }
        
    } catch (error) {
        removeLoadingIndicator(loadingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Error:', error);
    }
}

// Add message to chat
function addMessage(content, sender, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Main message content
    const textDiv = document.createElement('div');
    textDiv.textContent = content;
    contentDiv.appendChild(textDiv);
    
    // Add metadata if bot message
    if (sender === 'bot') {
        if (metadata.department) {
            const deptDiv = document.createElement('div');
            deptDiv.style.fontSize = '12px';
            deptDiv.style.color = '#666';
            deptDiv.style.marginTop = '5px';
            deptDiv.textContent = `Department: ${metadata.department}`;
            contentDiv.appendChild(deptDiv);
        }
        
        if (metadata.ticket_id) {
            const ticketDiv = document.createElement('div');
            ticketDiv.style.fontSize = '12px';
            ticketDiv.style.color = '#007bff';
            ticketDiv.style.marginTop = '5px';
            ticketDiv.textContent = `Ticket created: ${metadata.ticket_id}`;
            contentDiv.appendChild(ticketDiv);
        }
        
        if (metadata.sources && metadata.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong>';
            
            metadata.sources.forEach(source => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                sourceItem.textContent = `• ${source.title} (${Math.round(source.score * 100)}% match)`;
                sourcesDiv.appendChild(sourceItem);
            });
            
            contentDiv.appendChild(sourcesDiv);
        }
    }
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Loading indicator
function addLoadingIndicator() {
    const loadingId = 'loading_' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message bot';
    loadingDiv.innerHTML = '<div class="message-content"><div class="loading"></div></div>';
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return loadingId;
}

function removeLoadingIndicator(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Load recent tickets
async function loadRecentTickets() {
    try {
        const response = await fetch(`${API_URL}/tickets/user/demo_user`);
        const tickets = await response.json();
        
        ticketList.innerHTML = '';
        tickets.slice(0, 5).forEach(ticket => {
            const ticketDiv = document.createElement('div');
            ticketDiv.className = 'ticket-item';
            ticketDiv.innerHTML = `
                <div style="font-weight: bold">${ticket.title}</div>
                <div style="font-size: 12px; color: #666">
                    <span class="ticket-status ${ticket.status}">${ticket.status}</span>
                    • ${new Date(ticket.created_at).toLocaleDateString()}
                </div>
            `;
            ticketDiv.addEventListener('click', () => viewTicket(ticket.id));
            ticketList.appendChild(ticketDiv);
        });
        
        if (tickets.length === 0) {
            ticketList.innerHTML = '<p style="color: #666">No tickets yet</p>';
        }
        
    } catch (error) {
        console.error('Error loading tickets:', error);
    }
}

// View ticket details
function viewTicket(ticketId) {
    window.open(`http://localhost:8080/ticket/zoom/${ticketId}`, '_blank');
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    addMessage('Hello! I\'m your AI helpdesk assistant. How can I help you today?', 'bot');
    loadRecentTickets();
});