// CyberGuard Enterprise Platform - Main JavaScript

// Smooth scroll for navigation links
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

// Pricing toggle (Monthly/Annual)
const pricingToggle = document.querySelectorAll('.toggle-btn');
const priceAmounts = document.querySelectorAll('.price-amount[data-monthly]');

pricingToggle.forEach(btn => {
    btn.addEventListener('click', function() {
        const period = this.dataset.period;
        
        // Update active state
        pricingToggle.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // Update prices
        priceAmounts.forEach(price => {
            const monthly = price.dataset.monthly;
            const annual = price.dataset.annual;
            
            if (period === 'annual') {
                price.textContent = '$' + (annual / 12).toFixed(0);
            } else {
                price.textContent = '$' + monthly;
            }
        });
    });
});

// Contact form submission
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);
        
        // Simulate form submission
        console.log('Form submitted:', data);
        
        // Show success message
        alert('Thank you for contacting us! We will get back to you within 24 hours.');
        
        // Reset form
        this.reset();
        
        // In production, you would send this to your backend:
        // fetch('/api/contact', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(data)
        // }).then(response => response.json())
        //   .then(data => console.log('Success:', data))
        //   .catch(error => console.error('Error:', error));
    });
}

// Mobile menu toggle
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navMenu = document.querySelector('.nav-menu');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        this.classList.toggle('active');
    });
}

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    } else {
        navbar.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
    }
    
    lastScroll = currentScroll;
});

// Threat chart animation (using Chart.js if available)
function initThreatChart() {
    const canvas = document.getElementById('threatChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Simple gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(0, 102, 255, 0.5)');
    gradient.addColorStop(1, 'rgba(0, 212, 255, 0.1)');
    
    // Draw simple area chart
    canvas.width = canvas.offsetWidth;
    canvas.height = 200;
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.moveTo(0, 200);
    
    // Generate random data points
    const points = 20;
    for (let i = 0; i <= points; i++) {
        const x = (canvas.width / points) * i;
        const y = 200 - Math.random() * 150 - 20;
        ctx.lineTo(x, y);
    }
    
    ctx.lineTo(canvas.width, 200);
    ctx.closePath();
    ctx.fill();
    
    // Draw line on top
    ctx.strokeStyle = '#0066ff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (let i = 0; i <= points; i++) {
        const x = (canvas.width / points) * i;
        const y = 200 - Math.random() * 150 - 20;
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    ctx.stroke();
}

// Initialize chart when page loads
window.addEventListener('load', initThreatChart);

// Counter animation for stats
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        if (element.textContent.includes('%')) {
            element.textContent = Math.floor(current) + '%';
        } else if (element.textContent.includes('+')) {
            element.textContent = Math.floor(current).toLocaleString() + '+';
        } else if (element.textContent.includes('K')) {
            element.textContent = '$' + Math.floor(current) + 'K+';
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

// Intersection Observer for animating elements on scroll
const observerOptions = {
    threshold: 0.2,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            
            // Animate counters
            if (entry.target.classList.contains('stat-number') || 
                entry.target.classList.contains('stat-value')) {
                const text = entry.target.textContent;
                const num = parseInt(text.replace(/[^0-9]/g, ''));
                if (num) {
                    animateCounter(entry.target, num);
                }
            }
            
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.feature-card, .stat-card, .pricing-card, .stat').forEach(el => {
    observer.observe(el);
});

// Add animation class to stats
document.querySelectorAll('.stat-number, .stat-value').forEach(el => {
    observer.observe(el);
});

// Signup modal functionality
function openSignupModal() {
    // In production, this would open a modal or redirect to signup page
    console.log('Opening signup modal...');
    alert('Signup functionality will redirect to registration page.\n\nFor demo purposes, contact sales@cyberguard-platform.com');
}

// Add event listeners to signup buttons
document.querySelectorAll('a[href="#signup"]').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        openSignupModal();
    });
});

// Demo functionality
function openDemo() {
    // In production, this would open a demo video or interactive demo
    console.log('Opening demo...');
    alert('Demo functionality will showcase:\n\n• Real-time threat detection\n• ML-powered analytics\n• Dashboard interface\n• Response automation\n\nContact us for a live demo!');
}

document.querySelectorAll('a[href="#demo"]').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        openDemo();
    });
});

// Parallax effect for hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroVisual = document.querySelector('.hero-visual');
    
    if (heroVisual) {
        heroVisual.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Add keyboard navigation
document.addEventListener('keydown', (e) => {
    // Escape key closes modals
    if (e.key === 'Escape') {
        // Close any open modals
        console.log('Escape pressed');
    }
});

// Performance optimization: Lazy load images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img.lazy').forEach(img => {
        imageObserver.observe(img);
    });
}

// Console welcome message
console.log('%c🛡️ CyberGuard Enterprise Platform', 'font-size: 20px; font-weight: bold; color: #0066ff;');
console.log('%cML-Powered Cybersecurity for Fortune 500 Companies', 'font-size: 14px; color: #00d4ff;');
console.log('%cInterested in our platform? Contact sales@cyberguard-platform.com', 'font-size: 12px; color: #666;');

// Analytics tracking (placeholder - replace with actual analytics)
function trackEvent(category, action, label) {
    console.log('Analytics Event:', { category, action, label });
    // In production, send to Google Analytics, Mixpanel, etc.
    // gtag('event', action, { 'event_category': category, 'event_label': label });
}

// Track button clicks
document.querySelectorAll('.btn-primary, .btn-secondary').forEach(btn => {
    btn.addEventListener('click', () => {
        trackEvent('Engagement', 'Button Click', btn.textContent);
    });
});

// Track pricing card interactions
document.querySelectorAll('.pricing-card').forEach((card, index) => {
    card.addEventListener('mouseenter', () => {
        trackEvent('Pricing', 'Card Hover', card.querySelector('.pricing-tier').textContent);
    });
});

// Service Worker registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js')
        //     .then(reg => console.log('Service Worker registered'))
        //     .catch(err => console.log('Service Worker registration failed'));
    });
}

// Form validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Add real-time validation to email inputs
document.querySelectorAll('input[type="email"]').forEach(input => {
    input.addEventListener('blur', function() {
        if (this.value && !validateEmail(this.value)) {
            this.style.borderColor = '#ff3d00';
            this.setCustomValidity('Please enter a valid email address');
        } else {
            this.style.borderColor = '';
            this.setCustomValidity('');
        }
    });
});

// Easter egg: Konami code
let konamiCode = [];
const konamiPattern = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode.splice(-konamiPattern.length - 1, konamiCode.length - konamiPattern.length);
    
    if (konamiCode.join('').includes(konamiPattern.join(''))) {
        console.log('%c🎮 KONAMI CODE ACTIVATED! 🎮', 'font-size: 24px; font-weight: bold; color: #00ff00;');
        console.log('%cYou found the easter egg! Contact us with code: CYBER-KONAMI-2025 for a special discount!', 'font-size: 14px; color: #0066ff;');
        alert('🎮 Easter Egg Found!\n\nYou discovered the Konami Code!\nContact sales@cyberguard-platform.com with code: CYBER-KONAMI-2025 for a special discount!');
        konamiCode = [];
    }
});
