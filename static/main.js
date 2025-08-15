class MainAIInterface {
    constructor() {
        this.chatActive = false;
        this.recognition = null;
        this.isListening = false;
        this.screenshotData = null; // New variable to store screenshot data

        this.init();
    }

    init() {
        // Get DOM elements
        this.detachBtn = document.getElementById('detach-btn');
        this.settingsBtn = document.getElementById('settings-btn');

        this.takeScreenshotCard = document.getElementById('take-screenshot');
        this.voiceInputCard = document.getElementById('voice-input');
        this.textChatCard = document.getElementById('text-chat');

        this.chatSection = document.getElementById('chat-section');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-btn');

        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');

        // Setup event listeners
        this.setupEventListeners();

        // Initialize speech recognition
        this.initSpeechRecognition();
    }

    setupEventListeners() {
        // Header buttons
        this.detachBtn.addEventListener('click', () => this.openDetachedMode());
        this.settingsBtn.addEventListener('click', () => this.openSettings());

        // Action cards
        this.takeScreenshotCard.addEventListener('click', () => this.handleScreenshot());
        this.voiceInputCard.addEventListener('click', () => this.handleVoiceInput());
        this.textChatCard.addEventListener('click', () => this.showChat());

        // Chat functionality
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize chat input
        this.chatInput.addEventListener('input', () => this.autoResizeInput());
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isListening = true;
                this.voiceInputCard.style.background = 'rgba(74, 144, 226, 0.3)';
                this.showStatus('Listening... Speak now');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleVoiceResult(transcript);
            };

            this.recognition.onerror = (event) => {
                this.showStatus('Speech recognition error: ' + event.error, 3000);
                this.stopListening();
            };

            this.recognition.onend = () => {
                this.stopListening();
            };
        }
    }

    openDetachedMode() {
        // Open detached interface in a new window
        const detachedWindow = window.open(
            '/detached',
            'AI Assistant',
            'width=400,height=100,resizable=yes,alwaysOnTop=yes,frame=no,transparent=yes'
        );

        if (detachedWindow) {
            // Close current window after a short delay
            setTimeout(() => {
                window.close();
            }, 1000);
        } else {
            this.showStatus('Please allow pop-ups to use detached mode', 3000);
        }
    }

    openSettings() {
        // For now, show a simple alert. In a full implementation, this would open a settings modal
        alert('Settings functionality would be implemented here. This would include personal context, preferences, API keys, etc.');
    }

    async handleScreenshot() {
        try {
            this.showStatus('Taking screenshot...');

            // First, ask the backend to take a screenshot and return the data
            const response = await fetch('/api/screenshot', {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Failed to take screenshot');

            const data = await response.json();

            if (data.success) {
                // Store the screenshot data
                this.screenshotData = data.screenshot;
                this.showChat();
                this.addMessage('Screenshot captured! What would you like to know about what\'s on your screen?', 'ai');
                this.chatInput.focus();
                this.hideStatus();
            } else {
                throw new Error(data.error || 'Screenshot failed');
            }
        } catch (error) {
            this.showStatus('Error: ' + error.message, 3000);
        }
    }

    handleVoiceInput() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (this.recognition) {
            this.recognition.start();
        } else {
            this.showStatus('Speech recognition not supported in this browser', 3000);
        }
    }

    stopListening() {
        this.isListening = false;
        this.voiceInputCard.style.background = '';
        this.hideStatus();
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    async handleVoiceResult(transcript) {
        this.showChat();
        this.addMessage(transcript, 'user');

        try {
            this.showStatus('Processing your request...');

            // Send query and screenshot data
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: transcript,
                    screenshot_data: this.screenshotData // Pass the stored screenshot data
                })
            });

            if (!response.ok) throw new Error('Failed to process request');

            const data = await response.json();

            if (data.success) {
                this.addMessage(data.response, 'ai');
            } else {s``
                throw new Error('Processing failed');
            }
        } catch (error) {
            this.addMessage('Sorry, I encountered an error: ' + error.message, 'ai');
        } finally {
            this.hideStatus();
            this.screenshotData = null; // Clear the stored data after use
        }
    }

    showChat() {
        this.chatActive = true;
        this.chatSection.classList.add('active');
        this.chatInput.focus();

        // Scroll to chat section
        this.chatSection.scrollIntoView({ behavior: 'smooth' });
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        this.chatInput.value = '';
        this.autoResizeInput();

        try {
            this.showStatus('Processing...');

            // Send query and screenshot data
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: message,
                    screenshot_data: this.screenshotData // Pass the stored screenshot data
                })
            });

            if (!response.ok) throw new Error('Failed to send message');

            const data = await response.json();

            if (data.success) {
                this.addMessage(data.response, 'ai');
            } else {
                throw new Error('Processing failed');
            }
        } catch (error) {
            this.addMessage('Sorry, I encountered an error: ' + error.message, 'ai');
        } finally {
            this.hideStatus();
            this.screenshotData = null; // Clear the stored data after use
        }
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = content;

        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;

        // Add animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';

        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
    }

    autoResizeInput() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }

    showStatus(message, duration = null) {
        this.statusText.textContent = message;
        this.statusIndicator.classList.remove('hidden');
        this.statusIndicator.classList.add('visible');

        if (duration) {
            setTimeout(() => this.hideStatus(), duration);
        }
    }

    hideStatus() {
        this.statusIndicator.classList.remove('visible');
        this.statusIndicator.classList.add('hidden');
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.mainInterface = new MainAIInterface();
});

// Handle page visibility for better speech recognition
document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.mainInterface && window.mainInterface.isListening) {
        window.mainInterface.stopListening();
    }
});
