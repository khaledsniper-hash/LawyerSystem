/* ========================================
   Main JS - Mizan Al-Adala
   ======================================== */

(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        var sidebar = document.getElementById('sidebar');
        var overlay = document.getElementById('sidebarOverlay');
        var toggle = document.getElementById('sidebarToggle');
        var closeBtn = document.getElementById('sidebarClose');
        
        if (toggle) {
            toggle.addEventListener('click', function() {
                sidebar.classList.add('show');
                overlay.classList.add('show');
            });
        }
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                sidebar.classList.remove('show');
                overlay.classList.remove('show');
            });
        }
        
        if (overlay) {
            overlay.addEventListener('click', function() {
                sidebar.classList.remove('show');
                overlay.classList.remove('show');
            });
        }
    });
})();