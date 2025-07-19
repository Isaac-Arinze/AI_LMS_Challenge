// Authentication JavaScript
let currentUser = null;

// Check if user is logged in on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    setupNavigation();
});

function checkAuthStatus() {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('userData');
    
    if (token && userData) {
        try {
        currentUser = JSON.parse(userData);
            showLoggedInNav();
            updateUserInterface();
        } catch (error) {
            console.error('Error parsing user data:', error);
            logout();
        }
    } else {
        showLoggedOutNav();
    }
}

function showLoggedInNav() {
    document.getElementById('navMenu').style.display = 'none';
    document.getElementById('loggedInNav').style.display = 'flex';
    
    // Update user name
    if (currentUser && currentUser.full_name) {
        document.getElementById('userName').textContent = currentUser.full_name;
    }
}

function showLoggedOutNav() {
    document.getElementById('navMenu').style.display = 'flex';
    document.getElementById('loggedInNav').style.display = 'none';
}

function updateUserInterface() {
    // Show/hide sections based on authentication
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        if (section.id === 'home' || section.id === 'features' || section.id === 'testimonials' || section.id === 'cta') {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    });
}

function setupNavigation() {
    // Add click event listeners to all nav links
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('nav-link')) {
            e.preventDefault();
            const href = e.target.getAttribute('href');
            const sectionId = href.substring(1);
            navigateToSection(sectionId);
        }
    });
}

function navigateToSection(sectionId) {
    console.log('Navigating to section:', sectionId);
    
    // Hide all sections first
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show the selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
        
        // Scroll to section
        targetSection.scrollIntoView({ behavior: 'smooth' });
        
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Find and activate the clicked link
        const clickedLink = document.querySelector(`[href="#${sectionId}"]`);
        if (clickedLink) {
            clickedLink.classList.add('active');
        }
        
        // Initialize specific sections if needed
        if (sectionId === 'chat' && typeof initChat === 'function') {
            initChat();
        }
        if (sectionId === 'dashboard' && typeof window.dashboard !== 'undefined') {
            window.dashboard.loadDashboardData();
        }
        if (sectionId === 'studyGroups' && typeof window.studyGroups !== 'undefined') {
            window.studyGroups.loadGroups();
        }
        if (sectionId === 'quiz' && typeof window.quiz !== 'undefined') {
            // Quiz is already initialized
        }
    } else {
        console.error('Section not found:', sectionId);
    }
}

// Login form submission
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    console.log('Login attempt:', { email, password: '***' });
    
    // Validate required fields
    if (!email || !password) {
        showNotification('Please enter both email and password', 'error');
        return;
    }
    
    try {
        const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: email,  // Backend expects 'username' but accepts email
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('userData', JSON.stringify(data.user));
            currentUser = data.user;
            
            showLoggedInNav();
            updateUserInterface();
            closeModal();
            
            // Show success message
            showNotification('Login successful! Welcome back.', 'success');
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Login failed. Please try again.', 'error');
    }
});

// Signup form submission
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('Signup form submitted');
    
    // Get form values directly from the input elements
    const userData = {
        full_name: document.getElementById('signupName').value,
        email: document.getElementById('signupEmail').value,
        username: document.getElementById('signupUsername').value,
        grade_level: document.getElementById('signupGrade').value,
        password: document.getElementById('signupPassword').value
    };
    
    console.log('Form data being sent:', userData);
    
    // Validate required fields
    if (!userData.full_name || !userData.email || !userData.username || !userData.grade_level || !userData.password) {
        console.log('Validation failed:', {
            full_name: !!userData.full_name,
            email: !!userData.email,
            username: !!userData.username,
            grade_level: !!userData.grade_level,
            password: !!userData.password
        });
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        console.log('Sending request to backend...');
        const response = await fetch('http://127.0.0.1:5000/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok) {
            showNotification('Registration successful! Please check your email to verify your account.', 'success');
            closeModal();
            // Switch to login form
            switchTab('login');
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('Registration failed. Please try again.', 'error');
    }
});

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    currentUser = null;
    
    showLoggedOutNav();
    updateUserInterface();
    
    // Reset forms
    document.getElementById('loginForm').reset();
    document.getElementById('signupForm').reset();
    
    showNotification('Logged out successfully', 'success');
}

function showLogin() {
    document.getElementById('authModal').style.display = 'block';
    switchTab('login');
}

function showSignup() {
    document.getElementById('authModal').style.display = 'block';
    switchTab('signup');
}

function closeModal() {
    document.getElementById('authModal').style.display = 'none';
}

function switchTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
    } else {
        loginForm.classList.add('hidden');
        signupForm.classList.remove('hidden');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('authModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Close modal when clicking X
document.querySelector('.close').onclick = closeModal;

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Initialize with home section visible
document.addEventListener('DOMContentLoaded', () => {
    if (!currentUser) {
        // For non-logged-in users, show only public sections
        const publicSections = ['home', 'features', 'testimonials', 'demo', 'cta'];
        const sections = document.querySelectorAll('section');
        sections.forEach(section => {
            if (publicSections.includes(section.id)) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }
});

// Test function for debugging
function testNav() {
    console.log('Testing navigation...');
    console.log('Current user:', currentUser);
    console.log('Token:', localStorage.getItem('token'));
    
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        console.log(`Section ${section.id}:`, section.style.display);
    });
    
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        console.log('Nav link:', link.textContent, link.href, link.style.display);
    });
    
    // Test clicking a nav link
    const dashboardLink = document.querySelector('[href="#dashboard"]');
    if (dashboardLink) {
        console.log('Found dashboard link, clicking...');
        dashboardLink.click();
    } else {
        console.log('Dashboard link not found');
    }
}

// Make test function global
window.testNav = testNav;