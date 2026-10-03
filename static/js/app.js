/**
 * VitalPath Education - Front-End Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons if available
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Mobile Navigation Drawer Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileNavDrawer = document.getElementById('mobile-nav-drawer');
    const mobileMenuClose = document.getElementById('mobile-menu-close');

    if (mobileMenuBtn && mobileNavDrawer) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileNavDrawer.classList.toggle('hidden');
            document.body.classList.toggle('overflow-hidden');
        });
    }

    if (mobileMenuClose && mobileNavDrawer) {
        mobileMenuClose.addEventListener('click', () => {
            mobileNavDrawer.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        });
    }

    // Accordion Toggle Handlers
    document.querySelectorAll('[data-accordion-toggle]').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-accordion-toggle');
            const content = document.getElementById(targetId);
            const icon = btn.querySelector('[data-accordion-icon]');
            
            if (content) {
                const isExpanded = !content.classList.contains('hidden');
                if (isExpanded) {
                    content.classList.add('hidden');
                    if (icon) icon.classList.remove('rotate-180');
                } else {
                    content.classList.remove('hidden');
                    if (icon) icon.classList.add('rotate-180');
                }
            }
        });
    });

    // Auto-dismiss alerts after 6 seconds
    document.querySelectorAll('.auto-dismiss-alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-8px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
});
