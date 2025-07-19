// Chat JavaScript
let chatInitialized = false;
let chatState = {
    isOpen: false,
    currentSession: null,
    messages: []
};

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Initialize chat when the chat section is accessed or when toggle is clicked
function initChat() {
    if (chatInitialized) return;
    
    const chatContainer = document.getElementById('chatContainer');
    const demoContainer = document.getElementById('demoContainer');
    
    if (!chatContainer && !demoContainer) return;
    
    chatInitialized = true;
    
    // Initialize chat interface
    setupChatInterface();
    
    // Load chat history if user is logged in
    if (localStorage.getItem('token')) {
        loadChatHistory();
    }
}

function setupChatInterface() {
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await sendQuestion();
        });
    }
    
    // Setup practice questions button
    setupPracticeQuestionsButton();
    
    // Add global function for onclick handlers
    window.generatePracticeQuestions = generatePracticeQuestions;
    window.generatePracticeQuestionsFromSelector = function() {
        const num = parseInt(document.getElementById('practiceNumQuestions')?.value) || 5;
        generatePracticeQuestions(num);
    };
    
    // Add welcome message
    if (chatMessages && chatMessages.children.length === 0) {
        addMessage('bot', `Hello, welcome to AI Tutor chat! What would you like to learn today?`);
    }
}

// Setup chat toggle functionality
function setupChatToggle() {
    const chatToggle = document.getElementById('chatToggle');
    const demoContainer = document.getElementById('demoContainer');
    const toggleText = document.getElementById('toggleText');
    
    if (chatToggle && demoContainer) {
        chatToggle.addEventListener('click', function() {
            if (demoContainer.style.display === 'none') {
                // Show chat
                demoContainer.style.display = 'block';
                toggleText.textContent = 'Close AI Chat';
                chatToggle.innerHTML = '<i class="fas fa-times"></i><span>Close AI Chat</span>';
                chatToggle.classList.add('active');
                chatState.isOpen = true;
                
                // Initialize chat if not already done
                initChat();
                
                // Re-setup practice questions button after chat is opened
                setTimeout(() => {
                    setupPracticeQuestionsButton();
                }, 100);
            } else {
                // Hide chat
                demoContainer.style.display = 'none';
                toggleText.textContent = 'Open AI Chat';
                chatToggle.innerHTML = '<i class="fas fa-comments"></i><span>Open AI Chat</span>';
                chatToggle.classList.remove('active');
                chatState.isOpen = false;
            }
        });
    }
}

function setupPracticeQuestionsButton() {
    // No-op: handled by the new selector/button
}

async function sendQuestion() {
    const questionInput = document.getElementById('questionInput');
    const subjectSelect = document.getElementById('subjectSelect');
    const topicInput = document.getElementById('topicInput');
    
    if (!questionInput || !subjectSelect || !topicInput) {
        console.error('Chat form elements not found');
        return;
    }
    
    const question = questionInput.value.trim();
    const subject = subjectSelect.value;
    const topic = topicInput.value.trim();
    
    if (!question) {
        showNotification('Please enter a question', 'error');
        return;
    }
    
    if (!subject) {
        showNotification('Please select a subject', 'error');
        return;
    }
    
    addMessage('user', question);
    
    questionInput.value = '';
    
    const loadingElem = addMessage('bot', 'Thinking...', true);
    
    try {
        const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Determine which endpoint to use based on authentication
        const endpoint = token ? 'http://127.0.0.1:5000/api/ai/ask' : 'http://127.0.0.1:5000/api/ai/demo/ask';
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        console.log('Sending question to:', endpoint);
        console.log('Request payload:', { question, subject, topic });
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                question: question,
                subject: subject,
                topic: topic
            })
        });
        
        const data = await response.json();
        console.log('AI response:', data);
        
        removeMessage(loadingElem);
        
        if (response.ok) {
            const botElem = addMessage('bot', data.response);
            
            // Add rating buttons only for authenticated users
            addRatingButtons(data.session_id);
        } else {
            addMessage('bot', `Sorry, I encountered an error: ${data.error || 'Unknown error'}. Please try again.`);
        }
    } catch (error) {
        console.error('Error sending question:', error);
        removeMessage(loadingElem);
        addMessage('bot', 'Sorry, I encountered an error. Please check your connection and try again.');
    }
}

function addMessage(sender, message, isLoading = false) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return null;
    // Remove any existing spinner before adding a new message
    Array.from(chatMessages.querySelectorAll('.loading-spinner')).forEach(spinner => spinner.parentElement?.parentElement?.remove());
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    if (isLoading) {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="loading-spinner" style="display: flex; align-items: center; gap: 8px;">
                    <span class="spinner-dot"></span>
                    <span class="spinner-dot"></span>
                    <span class="spinner-dot"></span>
                    <span style="font-size: 1.1em; color: #4a6bff; margin-left: 8px;">AI Tutor is thinking…</span>
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${message}</p>
            </div>
        `;
    }
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageDiv; // Return the element, not just the ID
}

function removeMessage(messageIdOrElem) {
    let message;
    if (typeof messageIdOrElem === 'string') {
        message = document.getElementById(messageIdOrElem);
    } else {
        message = messageIdOrElem;
    }
    if (message) {
        message.remove();
    }
}

function addRatingButtons(sessionId) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    // Remove any existing rating block
    Array.from(chatMessages.querySelectorAll('.rating-container')).forEach(rating => rating.remove());
    // Find the last bot message
    const botMessages = chatMessages.querySelectorAll('.message.bot-message');
    const lastBotMessage = botMessages[botMessages.length - 1];
    const ratingDiv = document.createElement('div');
    ratingDiv.className = 'rating-container';
    ratingDiv.innerHTML = `
        <p>Was this explanation helpful?</p>
        <div class="rating-buttons">
            <button onclick="window.rateResponseWrapper('${sessionId || ''}', 1)" class="rating-btn">
                <i class="fas fa-thumbs-down"></i>
                Not Helpful
            </button>
            <button onclick="window.rateResponseWrapper('${sessionId || ''}', 3)" class="rating-btn">
                <i class="fas fa-thumbs-up"></i>
                Helpful
            </button>
            <button onclick="window.rateResponseWrapper('${sessionId || ''}', 5)" class="rating-btn">
                <i class="fas fa-star"></i>
                Very Helpful
            </button>
        </div>
    `;
    // Insert after the last bot message, or at the end if not found
    if (lastBotMessage && lastBotMessage.nextSibling) {
        chatMessages.insertBefore(ratingDiv, lastBotMessage.nextSibling);
    } else {
        chatMessages.appendChild(ratingDiv);
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

window.rateResponseWrapper = function(sessionId, rating) {
    if (sessionId) {
        rateResponse(sessionId, rating);
    } else {
        showNotification('Thank you for your feedback!', 'success');
        // Remove rating buttons
        const ratingContainer = document.querySelector('.rating-container');
        if (ratingContainer) {
            ratingContainer.remove();
        }
    }
};

async function rateResponse(sessionId, rating) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/ai/rate/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ rating: rating })
        });
        
        if (response.ok) {
            showNotification('Thank you for your feedback!', 'success');
            
            // Remove rating buttons
            const ratingContainer = document.querySelector('.rating-container');
            if (ratingContainer) {
                ratingContainer.remove();
            }
        } else {
            showNotification('Error submitting rating', 'error');
        }
    } catch (error) {
        console.error('Error rating response:', error);
        showNotification('Error submitting rating', 'error');
    }
}

async function generatePracticeQuestions(numQuestions = 5) {
    console.log('generatePracticeQuestions called');
    const subjectSelect = document.getElementById('subjectSelect');
    const topicInput = document.getElementById('topicInput');
    const genBtn = document.querySelector('button[onclick*="generatePracticeQuestionsFromSelector"]');
    if (!subjectSelect || !topicInput) {
        console.error('Practice form elements not found');
        showNotification('Form elements not found', 'error');
        return;
    }
    const subject = subjectSelect.value;
    const topic = topicInput.value.trim();
    console.log('Practice question form values:', { subject, topic, numQuestions });
    if (!subject) {
        showNotification('Please select a subject', 'error');
        return;
    }
    if (!topic) {
        showNotification('Please enter a topic', 'error');
        return;
    }
    // Remove any existing spinner before adding a new one
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        Array.from(chatMessages.querySelectorAll('.loading-spinner')).forEach(spinner => spinner.parentElement?.parentElement?.remove());
    }
    // Disable the button while loading
    if (genBtn) genBtn.disabled = true;
    const loadingId = addMessage('bot', '', true); // Show spinner
    try {
        const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
        console.log('Using token for practice questions:', token ? 'Token found' : 'No token');
        const headers = { 'Content-Type': 'application/json' };
        const endpoint = token ? 'http://127.0.0.1:5000/api/ai/practice' : 'http://127.0.0.1:5000/api/ai/demo/practice';
        if (token) headers['Authorization'] = `Bearer ${token}`;
        console.log('Making API call to practice endpoint:', endpoint);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                subject: subject,
                topic: topic,
                num_questions: numQuestions
            })
        });
        const data = await response.json();
        // Remove all spinners before displaying questions
        if (chatMessages) {
            Array.from(chatMessages.querySelectorAll('.loading-spinner')).forEach(spinner => spinner.parentElement?.parentElement?.remove());
        }
        if (genBtn) genBtn.disabled = false;
        if (response.ok) {
            displayPracticeQuestions(data.questions);
            showNotification('Practice questions generated successfully!', 'success');
        } else {
            addMessage('bot', `Sorry, I encountered an error generating practice questions: ${data.error || 'Unknown error'}. Please try again.`);
            showNotification('Failed to generate practice questions', 'error');
        }
    } catch (error) {
        console.error('Error generating practice questions:', error);
        // Remove all spinners on error
        if (chatMessages) {
            Array.from(chatMessages.querySelectorAll('.loading-spinner')).forEach(spinner => spinner.parentElement?.parentElement?.remove());
        }
        if (genBtn) genBtn.disabled = false;
        addMessage('bot', 'Sorry, I encountered an error. Please check your connection and try again.');
        showNotification('Network error generating practice questions', 'error');
    }
}

function displayPracticeQuestions(questions) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    const questionsDiv = document.createElement('div');
    questionsDiv.className = 'practice-questions';
    questionsDiv.innerHTML = `
        <h4>Practice Questions:</h4>
        <div class="questions-list">
            ${questions.map((q, index) => {
                const explanation = q.explanation ? `<div class='question-explanation'><strong>Explanation:</strong> ${q.explanation}</div>` : `<div class='question-explanation'><em>No explanation provided.</em></div>`;
                return `
                    <div class="question-item">
                        <h5>Question ${index + 1}:</h5>
                        <p>${q.question}</p>
                        <div class="question-answer" style="display: none;">
                            ${explanation}
                        </div>
                        <button onclick="toggleAnswer(this)" class="btn btn-small">
                            Show Answer
                        </button>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    chatMessages.appendChild(questionsDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function toggleAnswer(button) {
    const answerDiv = button.previousElementSibling;
    if (answerDiv.style.display === 'none') {
        answerDiv.style.display = 'block';
        button.textContent = 'Hide Answer';
    } else {
        answerDiv.style.display = 'none';
        button.textContent = 'Show Answer';
    }
}

async function loadChatHistory() {
    try {
        const token = localStorage.getItem('token');
        if (!token) return;
        
        const response = await fetch('http://127.0.0.1:5000/api/ai/sessions', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.sessions && data.sessions.length > 0) {
                // Show recent sessions
                const recentSession = data.sessions[0];
                addMessage('bot', `Welcome back! Your last session was about ${recentSession.subject} - ${recentSession.topic}.`);
            }
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Initialize chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Setup chat toggle for home page
    setupChatToggle();
    
    // Check if we're on the chat section (for logged-in users)
    const chatSection = document.getElementById('chat');
    if (chatSection && chatSection.style.display !== 'none') {
        initChat();
    }

    // Add collapsible input form logic
    const toggleBtn = document.getElementById('toggleInputFormBtn');
    const inputFormSection = document.getElementById('inputFormSection');
    if (toggleBtn && inputFormSection) {
        toggleBtn.addEventListener('click', () => {
            if (inputFormSection.style.display === 'none') {
                inputFormSection.style.display = '';
                toggleBtn.textContent = 'Hide Input Form';
            } else {
                inputFormSection.style.display = 'none';
                toggleBtn.textContent = 'Show Input Form';
            }
        });
    }
});

// Export functions for global use
window.sendQuestion = sendQuestion;
window.rateResponse = rateResponse;
window.generatePracticeQuestions = generatePracticeQuestions;
window.toggleAnswer = toggleAnswer;
window.initChat = initChat;

// Test function for debugging
function testAITutor() {
    console.log('Testing AI Tutor...');
    
    // Test if elements exist
    const chatToggle = document.getElementById('chatToggle');
    const demoContainer = document.getElementById('demoContainer');
    const chatContainer = document.getElementById('chatContainer');
    
    console.log('Chat toggle:', chatToggle);
    console.log('Demo container:', demoContainer);
    console.log('Chat container:', chatContainer);
    
    // Test if chat is initialized
    console.log('Chat initialized:', chatInitialized);
    console.log('Chat state:', chatState);
    
    // Test form elements
    const questionInput = document.getElementById('questionInput');
    const subjectSelect = document.getElementById('subjectSelect');
    const topicInput = document.getElementById('topicInput');
    
    console.log('Question input:', questionInput);
    console.log('Subject select:', subjectSelect);
    console.log('Topic input:', topicInput);
    
    // Test practice questions button
    const practiceBtn = document.querySelector('button[onclick*="generatePracticeQuestions"]');
    console.log('Practice questions button:', practiceBtn);
    
    // Test if we can add a message
    if (questionInput && subjectSelect && topicInput) {
        console.log('Form elements found, testing message...');
        addMessage('bot', 'Test message from AI Tutor');
    }
    
    // Test token
    const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
    console.log('Token available:', !!token);
    
    // Test backend connection
    testBackendConnection();
    
    return {
        chatToggle: !!chatToggle,
        demoContainer: !!demoContainer,
        chatContainer: !!chatContainer,
        chatInitialized,
        formElements: !!(questionInput && subjectSelect && topicInput),
        practiceButton: !!practiceBtn,
        hasToken: !!token,
        chatState
    };
}

async function testBackendConnection() {
    console.log('Testing backend connection...');
    
    try {
        const response = await fetch('http://127.0.0.1:5000/health');
        if (response.ok) {
            console.log('✅ Backend is running');
            
            // Test demo endpoint
            const demoResponse = await fetch('http://127.0.0.1:5000/api/ai/demo/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subject: 'Mathematics',
                    topic: 'Algebra',
                    question: 'What is 2x + 3 = 7?'
                })
            });
            
            if (demoResponse.ok) {
                const data = await demoResponse.json();
                console.log('✅ Demo AI endpoint working:', data);
            } else {
                console.log('❌ Demo AI endpoint failed:', demoResponse.status);
            }
        } else {
            console.log('❌ Backend health check failed');
        }
    } catch (error) {
        console.log('❌ Backend connection failed:', error);
    }
}

// Make test function global
window.testAITutor = testAITutor;