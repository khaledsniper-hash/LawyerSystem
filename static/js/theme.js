/* ========================================
   Theme Toggle - Mizan Al-Adala
   ======================================== */

(function() {
    'use strict';
    
    // Load saved theme immediately
    var savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Initialize when DOM is ready
    function initThemeToggle() {
        var themeToggle = document.getElementById('themeToggle');
        
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                var current = document.documentElement.getAttribute('data-theme');
                var next = current === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', next);
                localStorage.setItem('theme', next);
                
                console.log('Theme changed to: ' + next);
            });
            
            console.log('Theme toggle initialized');
        } else {
            console.warn('Theme toggle button not found');
        }
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeToggle);
    } else {
        initThemeToggle();
    }
})();