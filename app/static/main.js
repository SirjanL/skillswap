function applyTheme(theme) {
    if (theme === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
}

function setTheme(theme) {
    localStorage.setItem('skillswap-theme', theme);
    applyTheme(theme);
    updateThemeButtons(theme);
}

function updateThemeButtons(theme) {
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
}

const savedTheme = localStorage.getItem('skillswap-theme') || 'dark';
applyTheme(savedTheme);

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (localStorage.getItem('skillswap-theme') === 'system') {
        applyTheme('system');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    updateThemeButtons(savedTheme);

    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => setTheme(btn.dataset.theme));
    });
});

// Auto-dismiss flash messages after 4 seconds
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
        a.style.transition = 'opacity 0.5s';
        a.style.opacity = '0';
        setTimeout(() => a.style.display = 'none', 500);
    });
}, 4000);

document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.href === window.location.href) {
        link.style.color = 'var(--text)';
        link.style.background = 'var(--surface2)';
        link.style.borderRadius = '8px';
    }
});

const thread = document.getElementById('message-thread');

function formatTime(isoString) {
    const date = new Date(isoString + 'Z');
    return date.toLocaleTimeString([], {
        hour:   '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

if (thread) {
    const exchangeId = thread.dataset.exchangeId;
    const currentUserId = parseInt(thread.dataset.exchangeId);

    function scrollBottom() {
        thread.scrollTop = thread.scrollHeight;
    }
    scrollBottom();

    function renderMessages(messages) {
        thread.innerHTML = '';
        let lastDate = null;

        messages.forEach(msg => {
            const msgDate = new Date(msg.time + 'Z');
            const dateStr = msgDate.toLocaleDateString([], {
                weekday: 'long',
                year:    'numeric',
                month:   'long',
                day:     'numeric'
            });

            if (dateStr !== lastDate) {
                lastDate = dateStr;
                const separator = document.createElement('div');
                separator.style.cssText = `
                    text-align:center; margin:1rem 0;
                    display:flex; align-items:center; gap:0.75rem;
                `;
                separator.innerHTML = `
                    <div style="flex:1; height:1px; background:#2e3248;"></div>
                    <span style="color:#7b809a; font-size:0.75rem; font-weight:600;
                                text-transform:uppercase; letter-spacing:0.06em;
                                white-space:nowrap;">
                        ${dateStr}
                    </span>
                    <div style="flex:1; height:1px; background:#2e3248;"></div>
                `;
                thread.appendChild(separator);
            }

            const wrapper = document.createElement('div');
            wrapper.style.cssText = `
                display:flex;
                justify-content:${msg.is_mine ? 'flex-end' : 'flex-start'};
                margin-bottom:0.8rem;
            `;

            const bubble = document.createElement('div');
            bubble.style.cssText = `
                max-width:70%; padding:0.6rem 1rem; border-radius:12px;
                background:${msg.is_mine ? '#7c6aff' : '#222536'};
                color:white;
            `;
            bubble.innerHTML = `
                <p style="margin:0; font-size:0.95rem;">${msg.content}</p>
                <p style="margin:0.3rem 0 0; font-size:0.7rem; opacity:0.7;">
                    ${formatTime(msg.time)}
                </p>
            `;

            wrapper.appendChild(bubble);
            thread.appendChild(wrapper);
        });

        scrollBottom();
    }
    function fetchMessages() {
        fetch(`/messages/${exchangeId}/poll`)
            .then(res => res.json())
            .then(data => renderMessages(data))
            .catch(err => console.error('Polling error:', err));
    }

    fetchMessages();
    setInterval(fetchMessages, 3000);

    const form = document.querySelector('#message-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = form.querySelector('input[name="content"]');
            const content = input.value.trim();
            if (!content) return;

            fetch(form.action, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `content=${encodeURIComponent(content)}`
            }).then(() => {
                input.value = '';
                fetchMessages();
            });
        });
    }
}

function pollNotifications() {
    fetch('/notifications/poll')
        .then(res => res.json())
        .then(data => {
            const badge = document.querySelector('.nav-bell .badge');
            const bellLink = document.querySelector('.nav-bell');

            if (data.count > 0) {
                if (badge) {
                    badge.textContent = data.count;
                } else {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'badge';
                    newBadge.textContent = data.count;
                    bellLink.appendChild(newBadge);
                }

                const latest = data.notifications[0];
                if (latest && latest.id !== lastNotifId) {
                    lastNotifId = latest.id;
                    showToast(latest);
                }
            } else {
                if (badge) badge.remove();
            }
        })
        .catch(err => console.error('Notification poll error:', err));
}

let lastNotifId = null;

function showToast(notification) {
    const existing = document.getElementById('notif-toast');
    if (existing) existing.remove();

    const icon =
        notification.type === 'new_request' ? '📨' :
        notification.type === 'accepted'    ? '✅' :
        notification.type === 'rejected'    ? '❌' : '🔔';

    const toast = document.createElement('div');
    toast.id = 'notif-toast';
    toast.style.cssText = `
        position: fixed;
        bottom: 1.5rem;
        right: 1.5rem;
        background: #1a1d27;
        border: 1px solid #2e3248;
        border-left: 4px solid #7c6aff;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        max-width: 320px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        z-index: 9999;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        animation: slideIn 0.3s ease;
        cursor: pointer;
        font-family: 'DM Sans', sans-serif;
    `;

    toast.innerHTML = `
        <span style="font-size:1.3rem;">${icon}</span>
        <div>
            <div style="font-weight:600; color:#eef0f8;
                        font-size:0.875rem; margin-bottom:0.2rem;">
                New Notification
            </div>
            <div style="color:#7b809a; font-size:0.82rem; line-height:1.4;">
                ${notification.message}
            </div>
        </div>
        <span style="color:#7b809a; font-size:1rem; margin-left:auto;
                     line-height:1;">✕</span>
    `;

    toast.addEventListener('click', () => {
        window.location.href = '/notifications';
    });

    document.body.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

pollNotifications();
setInterval(pollNotifications, 5000);