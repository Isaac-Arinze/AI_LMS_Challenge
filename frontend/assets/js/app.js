import { initAuth, showLogin, switchTab } from './auth.js';
import { initChat, sendQuestion, rateResponse, generatePracticeQuestions } from './chat.js';

// Main App JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    
    // Initialize mobile navigation
    initMobileNav();
    
    // Initialize smooth scrolling
    initSmoothScrolling();
    
    // Initialize animations
    initAnimations();
    
    // Test navigation
    testNavigation();
});

function testNavigation() {
    console.log('Testing navigation...');
    const navLinks = document.querySelectorAll('.nav-link');
    console.log('Found nav links:', navLinks.length);
    
    navLinks.forEach(link => {
        console.log('Nav link:', link.textContent, link.href);
    });
}

function initMobileNav() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const loggedInNav = document.getElementById('loggedInNav');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');
            
            // Toggle the appropriate nav menu
            if (loggedInNav.style.display === 'flex') {
                loggedInNav.classList.toggle('active');
            } else {
                navMenu.classList.toggle('active');
            }
        });
    }
}

function initSmoothScrolling() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function initAnimations() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .testimonial-card, .stat-card, .group-card, .progress-card').forEach(el => {
        observer.observe(el);
    });
}

// Utility functions
function scrollToDemo() {
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Global functions for external use
window.scrollToDemo = scrollToDemo;
window.scrollToTop = scrollToTop;