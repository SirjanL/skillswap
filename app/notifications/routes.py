from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.notifications import notifications
from app import db
from app.models import Notification
from flask import jsonify


# ── VIEW ALL NOTIFICATIONS ────────────────────────────────
@notifications.route('/notifications')
@login_required
def view_notifications():
    # Mark all as read when user opens the page
    unread = Notification.query.filter_by(
        user_id=current_user.user_id,
        is_read=False
    ).all()

    for n in unread:
        n.is_read = True
    db.session.commit()

    # Fetch all notifications newest first
    all_notifications = Notification.query.filter_by(
        user_id=current_user.user_id
    ).order_by(Notification.created_at.desc()).all()

    return render_template(
        'notifications/notifications.html',
        notifications=all_notifications
    )


# ── MARK SINGLE NOTIFICATION AS READ + REDIRECT ──────────
@notifications.route('/notifications/read/<int:notification_id>')
@login_required
def mark_read(notification_id):
    n = Notification.query.get_or_404(notification_id)

    if n.user_id != current_user.user_id:
        return redirect(url_for('notifications.view_notifications'))

    n.is_read = True
    db.session.commit()

    # Redirect to the relevant request if possible
    if n.request_id:
        return redirect(url_for(
            'requests_bp.request_detail',
            request_id=n.request_id
        ))

    return redirect(url_for('notifications.view_notifications'))


@notifications.route('/notifications/poll')
@login_required
def poll_notifications():
    unread = Notification.query.filter_by(
        user_id=current_user.user_id,
        is_read=False
    ).order_by(Notification.created_at.desc()).all()

    return jsonify({
        'count': len(unread),
        'notifications': [{
            'id':         n.notification_id,
            'message':    n.message,
            'type':       n.type,
            'request_id': n.request_id,
            'time':       n.created_at.isoformat()
        } for n in unread]
    })