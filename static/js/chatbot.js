// AyuMithra AI Chatbot - Multilingual Voice and Text Support

class AyuMithraChatbot {
    constructor() {
        this.chatWindow = document.getElementById('chatWindow');
        this.chatToggle = document.getElementById('chatToggle');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.voiceIndicator = document.getElementById('voiceIndicator');
        this.chatTyping = document.getElementById('chatTyping');
        this.languageSelect = document.getElementById('chatLanguage');
        
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isRecording = false;
        this.chatHistory = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initSpeechRecognition();
    }
    
    setupEventListeners() {
        // Toggle chat window
        this.chatToggle.addEventListener('click', () => this.toggleChat());
        
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Voice input
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
        
        // Language change
        this.languageSelect.addEventListener('change', () => {
            this.initSpeechRecognition();
        });
        
        // Speak buttons for bot messages
        this.chatMessages.addEventListener('click', (e) => {
            if (e.target.closest('.message-speak')) {
                const messageEl = e.target.closest('.chat-message').querySelector('.message-content');
                this.speakText(messageEl.textContent);
            }
        });
    }
    
    toggleChat() {
        this.chatWindow.classList.toggle('hidden');
        this.chatToggle.querySelector('.chat-icon-open').classList.toggle('hidden');
        this.chatToggle.querySelector('.chat-icon-close').classList.toggle('hidden');
        
        if (!this.chatWindow.classList.contains('hidden')) {
            this.chatInput.focus();
        }
    }
    
    initSpeechRecognition() {
        // First try browser's built-in Web Speech API (works better for most cases)
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                this.voiceBtn.classList.add('recording');
                this.voiceIndicator.classList.remove('hidden');
                this.chatInput.placeholder = this.getListeningText();
            };
            
            this.recognition.onend = () => {
                this.isRecording = false;
                this.voiceBtn.classList.remove('recording');
                this.voiceIndicator.classList.add('hidden');
                this.chatInput.placeholder = this.getPlaceholderText();
            };
            
            this.recognition.onresult = (event) => {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                if (finalTranscript) {
                    this.chatInput.value = finalTranscript;
                    this.sendMessage();
                } else if (interimTranscript) {
                    this.chatInput.value = interimTranscript;
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isRecording = false;
                this.voiceBtn.classList.remove('recording');
                this.voiceIndicator.classList.add('hidden');
                
                let errorMsg = 'Speech recognition error. Please try again.';
                if (event.error === 'no-speech') {
                    errorMsg = 'No speech detected. Please try again.';
                } else if (event.error === 'audio-capture') {
                    errorMsg = 'No microphone found. Please check your device.';
                } else if (event.error === 'not-allowed') {
                    errorMsg = 'Microphone access denied. Please allow access.';
                } else if (event.error === 'network') {
                    errorMsg = 'Network error. Please check your connection.';
                }
                
                this.addBotMessage(errorMsg);
            };
            
            this.useBrowserSpeech = true;
        } else {
            this.useBrowserSpeech = false;
            this.voiceBtn.style.display = 'none';
            console.warn('Speech recognition not supported in this browser');
        }
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                await this.transcribeAudio(audioBlob);
                
                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.voiceBtn.classList.add('recording');
            this.voiceIndicator.classList.remove('hidden');
            this.chatInput.placeholder = this.getListeningText();
            
        } catch (error) {
            console.error('Microphone error:', error);
            let errorMsg = 'Could not access microphone. Please check permissions.';
            if (error.name === 'NotAllowedError') {
                errorMsg = 'Microphone access denied. Please allow access in browser settings.';
            } else if (error.name === 'NotFoundError') {
                errorMsg = 'No microphone found. Please connect a microphone.';
            }
            this.addBotMessage(errorMsg);
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.voiceBtn.classList.remove('recording');
            this.voiceIndicator.classList.add('hidden');
            this.chatInput.placeholder = this.getPlaceholderText();
        }
    }
    
    async transcribeAudio(audioBlob) {
        try {
            this.chatInput.placeholder = 'Transcribing...';
            
            // Convert blob to base64
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            
            reader.onloadend = async () => {
                const base64Audio = reader.result;
                
                // Send to server for transcription
                const response = await fetch('/transcribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        audio: base64Audio,
                        language: this.languageSelect.value
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.chatInput.value = data.transcript;
                    this.sendMessage();
                } else {
                    this.addBotMessage(data.error || 'Could not understand audio. Please try again or type your message.');
                }
                
                this.chatInput.placeholder = this.getPlaceholderText();
            };
            
        } catch (error) {
            console.error('Transcription error:', error);
            this.addBotMessage('Error transcribing audio. Please try again.');
            this.chatInput.placeholder = this.getPlaceholderText();
        }
    }
    
    toggleVoiceInput() {
        if (!this.useBrowserSpeech) {
            alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Firefox.');
            return;
        }
        
        if (this.isRecording) {
            this.recognition.stop();
        } else {
            this.recognition.lang = this.languageSelect.value;
            this.recognition.start();
        }
    }
    
    getListeningText() {
        const lang = this.languageSelect.value;
        const texts = {
            'en-US': 'Listening...',
            'hi-IN': 'सुन रहा हूँ...',
            'te-IN': 'వింటున్నాను...'
        };
        return texts[lang] || 'Listening...';
    }
    
    getPlaceholderText() {
        const lang = this.languageSelect.value;
        const texts = {
            'en-US': 'Type your health question...',
            'hi-IN': 'अपना स्वास्थ्य प्रश्न लिखें...',
            'te-IN': 'మీ ఆరోగ్య ప్రశ్నను టైప్ చేయండి...'
        };
        return texts[lang] || 'Type your health question...';
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        this.addUserMessage(message);
        this.chatInput.value = '';
        
        // Show typing indicator
        this.chatTyping.classList.remove('hidden');
        
        // Get bot response
        try {
            const response = await this.getBotResponse(message);
            this.chatTyping.classList.add('hidden');
            this.addBotMessage(response);
            
            // Auto-speak response if voice was used
            if (this.isRecording || this.shouldAutoSpeak()) {
                this.speakText(response);
            }
        } catch (error) {
            this.chatTyping.classList.add('hidden');
            this.addBotMessage('Sorry, I encountered an error. Please try again.');
        }
    }
    
    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">${this.escapeHtml(text)}</div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        this.chatHistory.push({ role: 'user', content: text });
    }
    
    addBotMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content">${text}</div>
            <button class="message-speak" title="Read aloud">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                </svg>
            </button>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        this.chatHistory.push({ role: 'assistant', content: text });
    }
    
    async getBotResponse(message) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    language: this.languageSelect.value,
                    history: this.chatHistory.slice(-5) // Last 5 messages for context
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // If symptoms were detected, offer to analyze
                if (data.symptoms_detected && data.symptoms_detected.length > 0) {
                    this.highlightSymptoms(data.symptoms_detected);
                }
                
                // Log translation info for debugging
                if (data.translated_message) {
                    console.log(`Translated "${message}" (${data.detected_input_language}) to: "${data.translated_message}"`);
                }
                
                return data.response;
            } else {
                return data.error || 'Sorry, I could not process your request.';
            }
        } catch (error) {
            console.error('Chat API error:', error);
            return this.getFallbackResponse(message);
        }
    }
    
    getFallbackResponse(message) {
        const lowerMsg = message.toLowerCase();
        
        // Simple keyword-based responses for offline mode
        if (lowerMsg.includes('fever') || lowerMsg.includes('temperature')) {
            return 'Fever can be a symptom of various conditions including flu, COVID-19, dengue, or malaria. Please use our symptom checker for a more accurate assessment.';
        }
        if (lowerMsg.includes('headache') || lowerMsg.includes('head pain')) {
            return 'Headaches can be caused by migraines, tension, or other conditions. If severe or persistent, please consult a doctor.';
        }
        if (lowerMsg.includes('cough') || lowerMsg.includes('cold')) {
            return 'Cough and cold symptoms could indicate common cold, flu, or COVID-19. Please check your symptoms using our analyzer.';
        }
        if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
            return 'Hello! How can I help you with your health concerns today?';
        }
        if (lowerMsg.includes('thank')) {
            return 'You\'re welcome! Take care of your health.';
        }
        
        return 'I understand you have a health question. Please use our symptom checker tool for a detailed analysis, or consult a healthcare professional for medical advice.';
    }
    
    speakText(text) {
        if (!this.synthesis) return;
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = this.languageSelect.value;
        utterance.rate = 0.9;
        utterance.pitch = 1;
        
        this.synthesis.speak(utterance);
    }
    
    shouldAutoSpeak() {
        // Auto-speak if the last interaction was voice-based
        return this.chatHistory.length > 0 && 
               this.chatHistory[this.chatHistory.length - 1].role === 'user';
    }
    
    highlightSymptoms(symptoms) {
        // Could highlight symptoms in the symptom checker grid
        console.log('Detected symptoms:', symptoms);
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ayuMithraChatbot = new AyuMithraChatbot();
});
