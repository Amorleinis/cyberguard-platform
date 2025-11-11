/**
 * CyberGuard Enterprise Platform - Web Application
 * Main JavaScript Application Logic
 */

// Configuration
const CONFIG = {
    API_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000',
    AUTO_REFRESH: 5000, // 5 seconds
};

// Application State
const state = {
    user: null,
    threats: [],
    stats: {},
    websocket: null,
    authenticated: false,
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    console.log('🛡️ CyberGuard Platform Initializing...');
    
    // Check authentication
    const token = localStorage.getItem('auth_token');
    if (token) {
        verifyToken(token);
    } else {
        showLoginModal();
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // Load settings
    loadSettings();
    
    // Hide loading screen
    setTimeout(() => {
        document.getElementById('loading-screen').classList.add('hidden');
    }, 1500);
});

// Authentication
function showLoginModal() {
    const modal = document.getElementById('login-modal');
    modal.style.display = 'flex';
}

function hideLoginModal() {
    const modal = document.getElementById('login-modal');
    modal.style.display = 'none';
}

function verifyToken(token) {
    // In demo mode, accept any token
    state.authenticated = true;
    state.user = {
        name: 'Admin User',
        email: 'admin@cyberguard.com',
        role: 'Administrator'
    };
    
    document.getElementById('user-name').textContent = state.user.name;
    document.getElementById('app').classList.remove('hidden');
    
    // Start the application
    startApplication();
}

async function login(email, password) {
    try {
        // Demo mode - accept any credentials
        const token = 'demo-token-' + Date.now();
        localStorage.setItem('auth_token', token);
        
        state.authenticated = true;
        state.user = {
            name: email.split('@')[0],
            email: email,
            role: 'Administrator'
        };
        
        hideLoginModal();
        document.getElementById('app').classList.remove('hidden');
        document.getElementById('user-name').textContent = state.user.name;
        
        startApplication();
        
        return true;
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please try again.');
        return false;
    }
}

function logout() {
    localStorage.removeItem('auth_token');
    state.authenticated = false;
    state.user = null;
    
    if (state.websocket) {
        state.websocket.close();
    }
    
    location.reload();
}

// Application Startup
function startApplication() {
    console.log('✅ Application started');
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Load initial data
    loadDashboardData();
    
    // Start auto-refresh
    setInterval(() => {
        if (state.authenticated) {
            loadDashboardData();
        }
    }, CONFIG.AUTO_REFRESH);
    
    // Initialize chart
    initializeChart();
}

// WebSocket Connection
function connectWebSocket() {
    try {
        const wsUrl = `${CONFIG.WS_URL}/ws/threats`;
        state.websocket = new WebSocket(wsUrl);
        
        state.websocket.onopen = () => {
            console.log('🔌 WebSocket connected');
            updateConnectionStatus(true);
        };
        
        state.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        state.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };
        
        state.websocket.onclose = () => {
            console.log('🔌 WebSocket disconnected');
            updateConnectionStatus(false);
            
            // Reconnect after 5 seconds
            setTimeout(() => {
                if (state.authenticated) {
                    connectWebSocket();
                }
            }, 5000);
        };
    } catch (error) {
        console.error('WebSocket connection error:', error);
        updateConnectionStatus(false);
    }
}

function handleWebSocketMessage(data) {
    console.log('📨 WebSocket message:', data);
    
    if (data.type === 'threat') {
        addThreat(data.threat);
        updateThreatBadge();
    } else if (data.type === 'notification') {
        showNotification(data.message);
    }
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const dot = statusElement.querySelector('.status-dot');
    const text = statusElement.querySelector('.status-text');
    
    if (connected) {
        dot.classList.remove('disconnected');
        text.textContent = 'Connected';
    } else {
        dot.classList.add('disconnected');
        text.textContent = 'Disconnected';
    }
}

// Dashboard Data
async function loadDashboardData() {
    try {
        // Try to fetch from backend API
        const response = await fetch(`${CONFIG.API_URL}/api/v1/dashboard`);
        
        if (response.ok) {
            const data = await response.json();
            updateDashboard(data);
        } else {
            // Use demo data if API not available
            useDemoData();
        }
    } catch (error) {
        console.log('API not available, using demo data');
        useDemoData();
    }
}

function useDemoData() {
    const demoData = {
        active_threats: Math.floor(Math.random() * 10),
        blocked_threats: Math.floor(Math.random() * 1000) + 500,
        system_health: 95 + Math.floor(Math.random() * 5),
        network_traffic: (Math.random() * 10).toFixed(2),
        cpu_usage: 40 + Math.floor(Math.random() * 20),
        memory_usage: 50 + Math.floor(Math.random() * 30),
        disk_usage: 30 + Math.floor(Math.random() * 20),
    };
    
    updateDashboard(demoData);
}

function updateDashboard(data) {
    // Update stats cards
    document.getElementById('active-threats').textContent = data.active_threats || 0;
    document.getElementById('blocked-threats').textContent = (data.blocked_threats || 0).toLocaleString();
    document.getElementById('system-health').textContent = (data.system_health || 100) + '%';
    document.getElementById('network-traffic').textContent = (data.network_traffic || 0) + ' MB/s';
    
    // Update resource meters
    updateMeter('cpu', data.cpu_usage || 45);
    updateMeter('memory', data.memory_usage || 62);
    updateMeter('disk', data.disk_usage || 38);
    
    // Update threat badge
    updateThreatBadge();
}

function updateMeter(type, value) {
    const meter = document.getElementById(`${type}-meter`);
    const valueLabel = document.getElementById(`${type}-value`);
    
    if (meter && valueLabel) {
        meter.style.width = value + '%';
        valueLabel.textContent = value + '%';
    }
}

function updateThreatBadge() {
    const badge = document.getElementById('threat-badge');
    badge.textContent = state.threats.length;
}

// Threats Management
function addThreat(threat) {
    state.threats.unshift(threat);
    
    // Limit to last 50 threats
    if (state.threats.length > 50) {
        state.threats = state.threats.slice(0, 50);
    }
    
    renderThreats();
}

function renderThreats() {
    const threatList = document.getElementById('threat-list');
    
    if (state.threats.length === 0) {
        threatList.innerHTML = '<div class="empty-state"><p>No recent threats detected. System is secure.</p></div>';
        return;
    }
    
    // Show last 10 threats on dashboard
    const recentThreats = state.threats.slice(0, 10);
    
    threatList.innerHTML = recentThreats.map(threat => `
        <div class="threat-item ${threat.severity || 'low'}">
            <div class="threat-info">
                <h4>${threat.type || 'Unknown Threat'}</h4>
                <p>${threat.description || 'No description available'}</p>
            </div>
            <div class="threat-time">${formatTime(threat.timestamp)}</div>
        </div>
    `).join('');
}

function formatTime(timestamp) {
    if (!timestamp) return 'Just now';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    return date.toLocaleDateString();
}

// Chart
let threatChart = null;

function initializeChart() {
    const ctx = document.getElementById('threat-chart');
    
    if (!ctx || !window.Chart) {
        console.log('Chart.js not available');
        return;
    }
    
    const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
    const data = Array.from({length: 24}, () => Math.floor(Math.random() * 20));
    
    threatChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Threats Detected',
                data: data,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                },
                x: {
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
}

// Navigation
function navigateToPage(pageName) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        }
    });
    
    // Update active page
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'threats': 'Threat Monitor',
        'analytics': 'Security Analytics',
        'intelligence': 'Threat Intelligence',
        'protection': 'Active Protection',
        'payments': 'Subscription & Payments',
        'settings': 'Settings'
    };
    
    document.getElementById('page-title').textContent = titles[pageName] || 'Dashboard';
}

// Settings
function loadSettings() {
    const savedApiUrl = localStorage.getItem('api_url');
    if (savedApiUrl) {
        CONFIG.API_URL = savedApiUrl;
        document.getElementById('api-url').value = savedApiUrl;
    }
}

function saveSettings() {
    const apiUrl = document.getElementById('api-url').value;
    localStorage.setItem('api_url', apiUrl);
    CONFIG.API_URL = apiUrl;
    
    alert('Settings saved successfully!');
}

// Notifications
function showNotification(message) {
    const badge = document.getElementById('notification-badge');
    const currentCount = parseInt(badge.textContent) || 0;
    badge.textContent = currentCount + 1;
    
    // You could add a toast notification here
    console.log('📢 Notification:', message);
}

// Event Listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = e.currentTarget.dataset.page;
            navigateToPage(page);
        });
    });
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            await login(email, password);
        });
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // Notifications button
    const notificationsBtn = document.getElementById('notifications-btn');
    if (notificationsBtn) {
        notificationsBtn.addEventListener('click', () => {
            alert('Notifications panel coming soon!');
            document.getElementById('notification-badge').textContent = '0';
        });
    }
    
    // Save settings button
    const saveSettingsBtn = document.getElementById('save-settings');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }
    
    // Threat filter
    const threatFilter = document.getElementById('threat-filter');
    if (threatFilter) {
        threatFilter.addEventListener('change', (e) => {
            console.log('Filter threats by:', e.target.value);
            // Implement filtering logic
        });
    }
}

// Export for global access
window.CyberGuard = {
    state,
    loadDashboardData,
    navigateToPage,
    addThreat,
};

console.log('✅ CyberGuard Platform Loaded');
