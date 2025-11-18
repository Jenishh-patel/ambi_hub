/**
 * Theme toggle functionality for Ambitious Hub
 */

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get saved theme from localStorage or use default
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
    
    // Update theme toggle button if exists
    updateThemeToggleButton(savedTheme);
});

// Apply theme to document
function applyTheme(theme) {
    const html = document.documentElement;
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Also update body class for additional styling
    document.body.className = `theme-${theme}`;
}

// Toggle theme
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    updateThemeToggleButton(newTheme);
}

// Update theme toggle button appearance
function updateThemeToggleButton(theme) {
    const toggleButtons = document.querySelectorAll('.theme-toggle');
    toggleButtons.forEach(btn => {
        btn.textContent = theme === 'dark' ? '🌓' : '🌙';
        btn.title = `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`;
    });
}

// Make toggleTheme available globally
window.toggleTheme = toggleTheme;

