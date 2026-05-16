// Auto-dismiss flash messages after 4 seconds
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
        a.style.transition = 'opacity 0.5s';
        a.style.opacity = '0';
        setTimeout(() => a.style.display = 'none', 500);
    });
}, 4000);

// Highlight active nav link
document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.href === window.location.href) {
        link.style.color = 'var(--text)';
        link.style.background = 'var(--surface2)';
        link.style.borderRadius = '8px';
    }
});