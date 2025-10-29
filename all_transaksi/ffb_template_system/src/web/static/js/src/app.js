/**
 * Main Application JavaScript
 * FFB Template System
 */

// Global variables
let isLoading = false;

// Utility functions
function showLoading(message = 'Loading...') {
    isLoading = true;
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');

    if (loadingText) {
        loadingText.textContent = message;
    }

    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    isLoading = false;
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

function showToast(message, type = 'info', duration = 3000) {
    // Simple toast notification (can be replaced with Toastr)
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';

    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, duration);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
        showLoading();
        const response = await fetch(url, finalOptions);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        hideLoading();
        return data;

    } catch (error) {
        hideLoading();
        console.error('API request failed:', error);
        showToast('Request failed: ' + error.message, 'danger');
        throw error;
    }
}

// Navigation handling
function initializeNavigation() {
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Active menu highlighting
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.nav-link');

    menuLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Form handling
function initializeForms() {
    // Auto-format date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });

    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form.id)) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'warning');
            }
        });
    });
}

// Data table initialization
function initializeDataTables() {
    const tables = document.querySelectorAll('table[data-table="datatable"]');
    tables.forEach(table => {
        if (typeof $ !== 'undefined' && $.fn.dataTable) {
            $(table).DataTable({
                responsive: true,
                pageLength: 25,
                order: [[0, 'desc']],
                language: {
                    search: "Search:",
                    lengthMenu: "Show _MENU_ entries",
                    info: "Showing _START_ to _END_ of _TOTAL_ entries",
                    paginate: {
                        first: "First",
                        last: "Last",
                        next: "Next",
                        previous: "Previous"
                    }
                }
            });
        }
    });
}

// Chart initialization
function initializeCharts() {
    const chartElements = document.querySelectorAll('canvas[data-chart]');
    chartElements.forEach(canvas => {
        const chartType = canvas.getAttribute('data-chart');
        const chartData = JSON.parse(canvas.getAttribute('data-chart-data') || '{}');

        if (typeof Chart !== 'undefined') {
            new Chart(canvas, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    }
                }
            });
        }
    });
}

// Theme handling
function initializeTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    document.body.setAttribute('data-theme', currentTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

// Auto-refresh functionality
function initializeAutoRefresh() {
    const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
    autoRefreshElements.forEach(element => {
        const interval = parseInt(element.getAttribute('data-auto-refresh')) || 30000;

        setInterval(() => {
            const url = element.getAttribute('data-refresh-url');
            if (url) {
                loadContent(url, element);
            }
        }, interval);
    });
}

function loadContent(url, targetElement) {
    apiRequest(url)
        .then(data => {
            if (typeof data.html !== 'undefined') {
                targetElement.innerHTML = data.html;
            }
        })
        .catch(error => {
            console.error('Failed to load content:', error);
        });
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeForms();
    initializeDataTables();
    initializeCharts();
    initializeTheme();
    initializeAutoRefresh();

    // Hide loading overlay
    hideLoading();

    // Show welcome message
    const showToastWelcome = sessionStorage.getItem('showToastWelcome');
    if (!showToastWelcome) {
        showToast('Welcome to FFB Template System', 'success');
        sessionStorage.setItem('showToastWelcome', 'true');
    }
});

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // Refresh data when page becomes visible again
        const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
        autoRefreshElements.forEach(element => {
            const url = element.getAttribute('data-refresh-url');
            if (url) {
                loadContent(url, element);
            }
        });
    }
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showToast('An unexpected error occurred', 'danger');
});

// Export functions for global use
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showToast = showToast;
window.apiRequest = apiRequest;
window.validateForm = validateForm;