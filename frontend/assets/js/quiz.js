// Quiz System JavaScript
class QuizSystem {
    constructor() {
        this.currentQuiz = null;
        this.currentAttempt = null;
        this.currentQuestionIndex = 0;
        this.answers = {};
        this.timer = null;
        this.timeRemaining = 0;
        this.isAuthenticated = false;
        this.lastQuizParams = null;
        
        this.initializeEventListeners();
        this.checkAuthentication();
    }
    
    initializeEventListeners() {
        console.log('Initializing event listeners...');
        
        // Quiz generation - try multiple selectors
        const generateBtn = document.getElementById('generateQuizBtn') || 
                           document.querySelector('[onclick*="generateQuiz"]') ||
                           document.querySelector('.btn[onclick*="generateQuiz"]');
        
        if (generateBtn) {
            console.log('Found generate quiz button:', generateBtn);
            
            // Remove any existing onclick attributes
            generateBtn.removeAttribute('onclick');
            
            // Add proper event listener
            generateBtn.addEventListener('click', (e) => {
                console.log('Generate quiz clicked');
                e.preventDefault();
                e.stopPropagation();
                this.generateQuiz();
            });
            
            // Also make it globally accessible
            window.generateQuiz = () => this.generateQuiz();
        } else {
            console.log('Generate quiz button not found, checking for alternative selectors...');
            
            // Try to find button by text content
            const allButtons = document.querySelectorAll('button');
            allButtons.forEach(btn => {
                if (btn.textContent.toLowerCase().includes('generate') && 
                    btn.textContent.toLowerCase().includes('quiz')) {
                    console.log('Found generate quiz button by text:', btn);
                    btn.addEventListener('click', (e) => {
                        console.log('Generate quiz clicked (found by text)');
                        e.preventDefault();
                        e.stopPropagation();
                        this.generateQuiz();
                    });
                }
            });
        }
        
        // Quiz interface
        const submitBtn = document.getElementById('submitQuizBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitQuiz());
        }
        
        const exitBtn = document.getElementById('exitQuizBtn');
        if (exitBtn) {
            exitBtn.addEventListener('click', () => this.exitQuiz());
        }
        
        const prevBtn = document.getElementById('prevQuestionBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousQuestion());
        }
        
        const nextBtn = document.getElementById('nextQuestionBtn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextQuestion());
        }
        
        // Results actions
        const retakeBtn = document.getElementById('retakeQuizBtn');
        if (retakeBtn) {
            retakeBtn.addEventListener('click', () => this.retakeQuiz());
        }
        
        const newQuizBtn = document.getElementById('newQuizBtn');
        if (newQuizBtn) {
            newQuizBtn.addEventListener('click', () => this.showQuizSetup());
        }
        
        // Add global functions for onclick handlers
        window.submitQuiz = () => this.submitQuiz();
        window.exitQuiz = () => this.exitQuiz();
        window.previousQuestion = () => this.previousQuestion();
        window.nextQuestion = () => this.nextQuestion();
        window.retakeQuiz = () => this.retakeQuiz();
        window.showQuizSetup = () => this.showQuizSetup();
    }
    
    checkAuthentication() {
        // Check for both possible token storage keys
        const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
        this.isAuthenticated = !!token;
        
        console.log('Authentication check:', { 
            hasToken: !!token, 
            token: localStorage.getItem('token'),
            authToken: localStorage.getItem('authToken'),
            auth_token: localStorage.getItem('auth_token')
        });
        
        if (!this.isAuthenticated) {
            this.showMessage('Please login to access quizzes', 'info');
        } else {
            console.log('User is authenticated');
        }
    }
    
    async testGeminiBackend(subject, topic, difficulty = 'medium', numQuestions = 5, examType = 'WAEC') {
        // Test the Gemini backend endpoint directly
        try {
            const response = await fetch('http://127.0.0.1:5000/api/quiz/test_gemini', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subject, topic, difficulty, num_questions: numQuestions, exam_type: examType })
            });
            const data = await response.json();
            if (response.ok) {
                console.log('Gemini backend test questions:', data.questions);
                this.showMessage('Gemini backend test successful! Check console for questions.', 'success');
            } else {
                this.showMessage(data.error || 'Gemini backend test failed', 'error');
            }
        } catch (error) {
            console.error('Error testing Gemini backend:', error);
            this.showMessage('Error testing Gemini backend. See console.', 'error');
        }
    }

    async generateQuiz(params) {
        console.log('generateQuiz method called');
        if (!this.isAuthenticated) {
            console.log('User not authenticated');
            this.showMessage('Please login to generate quizzes', 'error');
            return;
        }
        let subject, topic, difficulty, examType, numQuestions;
        if (params) {
            ({ subject, topic, difficulty, examType, numQuestions } = params);
        } else {
            subject = document.getElementById('quizSubject').value;
            topic = document.getElementById('quizTopic').value;
            difficulty = document.getElementById('quizDifficulty').value;
            examType = document.getElementById('quizExamType').value;
            numQuestions = parseInt(document.getElementById('quizQuestions')?.value) || 5;
        }
        console.log('Form values:', { subject, topic, difficulty, examType, numQuestions });
        if (!subject || !topic) {
            console.log('Missing subject or topic');
            this.showMessage('Please select a subject and enter a topic', 'error');
            return;
        }
        this.showLoading('Generating quiz questions...');
        try {
            const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
            const response = await fetch('http://127.0.0.1:5000/api/quiz/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    subject,
                    topic,
                    difficulty,
                    exam_type: examType,
                    num_questions: numQuestions
                })
            });
            const data = await response.json();
            if (response.ok) {
                this.currentQuiz = data.quiz;
                this.startQuiz();
            } else {
                this.showMessage(data.error || 'Failed to generate quiz', 'error');
            }
        } catch (error) {
            console.error('Error generating quiz:', error);
            this.showMessage('Failed to generate quiz. Please try again.', 'error');
        }
        this.lastQuizParams = { subject, topic, difficulty, examType, numQuestions };
    }
    
    async startQuiz() {
        try {
            const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
            const response = await fetch(`http://127.0.0.1:5000/api/quiz/start/${this.currentQuiz.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentAttempt = data.attempt_id;
                this.loadQuizQuestions();
                this.startTimer();
            } else {
                this.showMessage(data.error || 'Failed to start quiz', 'error');
            }
        } catch (error) {
            console.error('Error starting quiz:', error);
            this.showMessage('Failed to start quiz. Please try again.', 'error');
        }
    }
    
    async loadQuizQuestions() {
        try {
            const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
            const response = await fetch(`http://127.0.0.1:5000/api/quiz/${this.currentQuiz.id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentQuiz = data.quiz;
                this.showQuizInterface();
                this.displayQuestion(0);
                this.updateQuestionIndicators();
            } else {
                this.showMessage(data.error || 'Failed to load quiz', 'error');
            }
        } catch (error) {
            console.error('Error loading quiz:', error);
            this.showMessage('Failed to load quiz. Please try again.', 'error');
        }
    }
    
    showQuizInterface() {
        document.querySelector('.quiz-setup').style.display = 'none';
        document.getElementById('quizInterface').style.display = 'block';
        document.getElementById('quizResults').style.display = 'none';
        
        document.getElementById('quizTitle').textContent = this.currentQuiz.title;
        this.updateProgress();
    }
    
    displayQuestion(index) {
        if (index < 0 || index >= this.currentQuiz.questions.length) return;
        this.currentQuestionIndex = index;
        const question = this.currentQuiz.questions[index];
        // Display exam type and year if available
        const questionTextElem = document.getElementById('questionText');
        let meta = '';
        if (question.exam_type || question.exam_year) {
            meta = `<div class="exam-meta" style="font-size:1.1em;color:#3a4ca8;margin-bottom:0.5em;">
                ${question.exam_type ? question.exam_type : ''} ${question.exam_year ? question.exam_year : ''}
            </div>`;
        }
        questionTextElem.innerHTML = `${meta}<span>${question.question}</span>`;
        const optionsContainer = document.getElementById('questionOptions');
        optionsContainer.innerHTML = '';
        Object.entries(question.options).forEach(([letter, text]) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'option-item';
            optionDiv.dataset.option = letter;
            const isSelected = this.answers[index] === letter;
            if (isSelected) {
                optionDiv.classList.add('selected');
            }
            optionDiv.innerHTML = `
                <div class="option-letter">${letter}</div>
                <div class="option-text">${text}</div>
            `;
            optionDiv.addEventListener('click', () => this.selectOption(letter));
            optionsContainer.appendChild(optionDiv);
        });
        this.updateProgress();
        this.updateNavigationButtons();
    }
    
    selectOption(option) {
        this.answers[this.currentQuestionIndex] = option;
        
        // Update visual selection
        const options = document.querySelectorAll('.option-item');
        options.forEach(opt => opt.classList.remove('selected'));
        event.target.closest('.option-item').classList.add('selected');
        
        this.updateQuestionIndicators();
    }
    
    updateProgress() {
        const progress = document.getElementById('quizProgress');
        progress.textContent = `Question ${this.currentQuestionIndex + 1} of ${this.currentQuiz.questions.length}`;
    }
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevQuestionBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        
        prevBtn.disabled = this.currentQuestionIndex === 0;
        nextBtn.disabled = this.currentQuestionIndex === this.currentQuiz.questions.length - 1;
    }
    
    updateQuestionIndicators() {
        const indicatorsContainer = document.getElementById('questionIndicators');
        indicatorsContainer.innerHTML = '';
        
        for (let i = 0; i < this.currentQuiz.questions.length; i++) {
            const indicator = document.createElement('div');
            indicator.className = 'question-indicator';
            indicator.textContent = i + 1;
            
            if (i === this.currentQuestionIndex) {
                indicator.classList.add('current');
            } else if (this.answers[i]) {
                indicator.classList.add('answered');
            }
            
            indicator.addEventListener('click', () => this.displayQuestion(i));
            indicatorsContainer.appendChild(indicator);
        }
    }
    
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.displayQuestion(this.currentQuestionIndex - 1);
        }
    }
    
    nextQuestion() {
        if (this.currentQuestionIndex < this.currentQuiz.questions.length - 1) {
            this.displayQuestion(this.currentQuestionIndex + 1);
        }
    }
    
    startTimer() {
        this.timeRemaining = this.currentQuiz.time_limit * 60; // Convert to seconds
        this.updateTimerDisplay();
        
        this.timer = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            if (this.timeRemaining <= 0) {
                this.submitQuiz();
            }
        }, 1000);
    }
    
    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        const timerElement = document.getElementById('quizTimer');
        
        timerElement.textContent = `Time: ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Add warning classes
        timerElement.className = 'timer';
        if (this.timeRemaining <= 300) { // 5 minutes
            timerElement.classList.add('danger');
        } else if (this.timeRemaining <= 600) { // 10 minutes
            timerElement.classList.add('warning');
        }
    }
    
    async submitQuiz() {
        if (this.timer) {
            clearInterval(this.timer);
        }
        
        const timeTaken = (this.currentQuiz.time_limit * 60) - this.timeRemaining;
        
        try {
            const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
            const response = await fetch(`http://127.0.0.1:5000/api/quiz/submit/${this.currentAttempt}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    answers: this.answers,
                    time_taken: timeTaken
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showResults(data);
            } else {
                this.showMessage(data.error || 'Failed to submit quiz', 'error');
            }
        } catch (error) {
            console.error('Error submitting quiz:', error);
            this.showMessage('Failed to submit quiz. Please try again.', 'error');
        }
    }
    
    showResults(results) {
        document.getElementById('quizInterface').style.display = 'none';
        document.getElementById('quizResults').style.display = 'block';
        
        // Update score display
        document.getElementById('scorePercentage').textContent = `${Math.round(results.score)}%`;
        document.getElementById('correctAnswers').textContent = results.correct_answers;
        document.getElementById('totalQuestions').textContent = results.total_questions;
        
        const passStatus = document.getElementById('passStatus');
        if (results.passed) {
            passStatus.textContent = 'Congratulations! You passed!';
            passStatus.className = 'pass-status passed';
        } else {
            passStatus.textContent = 'Keep practicing! You can do better next time.';
            passStatus.className = 'pass-status failed';
        }
        
        // Show detailed results
        this.displayDetailedResults(results.detailed_results);
        // Re-attach retake and new quiz button event listeners
        const retakeBtn = document.getElementById('retakeQuizBtn');
        if (retakeBtn) {
            retakeBtn.onclick = () => this.retakeQuiz();
        }
        const newQuizBtn = document.getElementById('newQuizBtn');
        if (newQuizBtn) {
            newQuizBtn.onclick = () => this.showQuizSetup();
        }
    }
    
    displayDetailedResults(detailedResults) {
        const container = document.getElementById('detailedResults');
        container.innerHTML = '';
        
        detailedResults.forEach((result, index) => {
            const resultItem = document.createElement('div');
            resultItem.className = `result-item ${result.is_correct ? 'correct' : 'incorrect'}`;
            
            resultItem.innerHTML = `
                <div class="result-status ${result.is_correct ? 'correct' : 'incorrect'}">
                    ${result.is_correct ? '✓' : '✗'}
                </div>
                <div class="result-content">
                    <div class="result-question">${result.question}</div>
                    <div class="result-details">
                        Your answer: ${result.user_answer || 'Not answered'} | 
                        Correct answer: ${result.correct_answer}
                    </div>
                    ${result.explanation ? `<div class="result-explanation">${result.explanation}</div>` : ''}
                </div>
            `;
            
            container.appendChild(resultItem);
        });
    }
    
    exitQuiz() {
        if (confirm('Are you sure you want to exit? Your progress will be lost.')) {
            this.resetQuiz();
            this.showQuizSetup();
        }
    }
    
    retakeQuiz() {
        if (this.lastQuizParams) {
            this.generateQuiz(this.lastQuizParams);
        } else {
            this.showQuizSetup();
        }
    }
    
    showQuizSetup() {
        document.querySelector('.quiz-setup').style.display = 'block';
        document.getElementById('quizInterface').style.display = 'none';
        document.getElementById('quizResults').style.display = 'none';
        // Optionally reset form fields
        const form = document.querySelector('.quiz-form');
        if (form) form.reset();
        // Re-attach new quiz button event listener in case results section is hidden and shown again
        const newQuizBtn = document.getElementById('newQuizBtn');
        if (newQuizBtn) {
            newQuizBtn.onclick = () => this.showQuizSetup();
        }
    }
    
    resetQuiz() {
        this.currentQuiz = null;
        this.currentAttempt = null;
        this.currentQuestionIndex = 0;
        this.answers = {};
        
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
    
    showLoading(message) {
        const setup = document.querySelector('.quiz-setup');
        setup.innerHTML = `
            <div class="quiz-loading">
                <div class="spinner"></div>
                <span>${message}</span>
            </div>
        `;
    }
    
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `quiz-message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        const container = document.querySelector('.quiz-container');
        container.insertBefore(messageDiv, container.firstChild);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    // Test function for debugging
    testQuizSystem() {
        console.log('Testing Quiz System...');
        
        // Test if elements exist
        const generateBtn = document.getElementById('generateQuizBtn');
        const quizSubject = document.getElementById('quizSubject');
        const quizTopic = document.getElementById('quizTopic');
        const quizDifficulty = document.getElementById('quizDifficulty');
        const quizExamType = document.getElementById('quizExamType');
        const quizQuestions = document.getElementById('quizQuestions');
        
        console.log('Generate button:', generateBtn);
        console.log('Quiz subject:', quizSubject);
        console.log('Quiz topic:', quizTopic);
        console.log('Quiz difficulty:', quizDifficulty);
        console.log('Quiz exam type:', quizExamType);
        console.log('Quiz questions:', quizQuestions);
        
        // Test authentication
        console.log('Is authenticated:', this.isAuthenticated);
        
        // Test token
        const token = localStorage.getItem('token') || localStorage.getItem('authToken') || localStorage.getItem('auth_token');
        console.log('Token available:', !!token);
        
        // Test current state
        console.log('Current quiz:', this.currentQuiz);
        console.log('Current attempt:', this.currentAttempt);
        console.log('Current question index:', this.currentQuestionIndex);
        
        return {
            generateButton: !!generateBtn,
            formElements: !!(quizSubject && quizTopic && quizDifficulty && quizExamType && quizQuestions),
            isAuthenticated: this.isAuthenticated,
            hasToken: !!token,
            currentQuiz: !!this.currentQuiz,
            currentAttempt: !!this.currentAttempt,
            currentQuestionIndex: this.currentQuestionIndex
        };
    }
}

// Initialize quiz system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Quiz System...');
    window.quizSystem = new QuizSystem();
    
    // Add quiz navigation to main navigation
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        const quizLink = document.createElement('a');
        quizLink.href = '#quiz';
        quizLink.className = 'nav-link';
        quizLink.textContent = 'Quizzes';
        
        // Insert before the nav-actions div
        const navActions = navMenu.querySelector('.nav-actions');
        if (navActions) {
            navMenu.insertBefore(quizLink, navActions);
        } else {
            navMenu.appendChild(quizLink);
        }
    }
    
    // Debug: Check if elements exist
    const generateBtn = document.getElementById('generateQuizBtn');
    if (generateBtn) {
        console.log('Generate Quiz button found');
        
        // Add a simple test click handler
        generateBtn.addEventListener('click', (e) => {
            console.log('Generate Quiz button clicked');
            e.preventDefault();
            e.stopPropagation();
            
            // Test if the button is working
            console.log('Button click detected');
            
            if (window.quizSystem) {
                console.log('Quiz system found, calling generateQuiz');
                window.quizSystem.generateQuiz();
            } else {
                console.log('Quiz system not found');
            }
        });
        
        // Also add a simple test to show the button is clickable
        generateBtn.style.cursor = 'pointer';
        console.log('Generate Quiz button is now clickable');
    } else {
        console.log('Generate Quiz button not found');
    }
    
    // Add global test function
    window.testQuizSystem = function() {
        console.log('Testing quiz system...');
        if (window.quizSystem) {
            console.log('Quiz system is available');
            
            // Check authentication
            const token = localStorage.getItem('authToken') || localStorage.getItem('auth_token');
            console.log('Authentication status:', !!token);
            
            // Test backend connection
            fetch('http://127.0.0.1:5000/health')
                .then(response => response.json())
                .then(data => {
                    console.log('Backend health check:', data);
                    const authStatus = token ? 'Authenticated' : 'Not authenticated';
                    alert(`Quiz system is working! Backend is running. ${authStatus}`);
                })
                .catch(error => {
                    console.error('Backend health check failed:', error);
                    alert('Quiz system is working but backend might not be running. Check console for details.');
                });
            
            return true;
        } else {
            console.log('Quiz system not available');
            alert('Quiz system not available. Check console for details.');
            return false;
        }
    };
    
    // Add a simple test for the generate quiz button
    window.testGenerateQuiz = function() {
        console.log('Testing generate quiz button...');
        const generateBtn = document.getElementById('generateQuizBtn');
        if (generateBtn) {
            console.log('Generate quiz button found');
            generateBtn.click();
            return true;
        } else {
            console.log('Generate quiz button not found');
            return false;
        }
    };
    
    console.log('Quiz System initialization complete');
}); 