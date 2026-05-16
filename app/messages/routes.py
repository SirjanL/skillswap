from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.messages import messages
from app import db
from app.models import Message, Exchange, Request, User


# ── MESSAGES INBOX ────────────────────────────────────────
@messages.route('/messages')
@login_required
def inbox():
    exchanges = Request.query.filter(
        Request.status == 'accepted',
        db.or_(
            Request.sender_id   == current_user.user_id,
            Request.receiver_id == current_user.user_id
        )
    ).all()

    # Deduplicate — keep only one conversation per other user
    seen_user_ids = set()
    conversations = []

    for req in exchanges:
        other = (
            req.receiver
            if req.sender_id == current_user.user_id
            else req.sender
        )

        if other.user_id in seen_user_ids:
            continue
        seen_user_ids.add(other.user_id)

        last_msg = Message.query.filter_by(
            exchange_id=req.exchange.exchange_id
        ).order_by(Message.timestamp.desc()).first()

        unread = Message.query.filter_by(
            exchange_id=req.exchange.exchange_id,
            receiver_id=current_user.user_id,
            is_read=False
        ).count()

        conversations.append({
            'exchange': req.exchange,
            'other':    other,
            'last_msg': last_msg,
            'unread':   unread
        })

    return render_template('messages/inbox.html', conversations=conversations)



# ── CONVERSATION VIEW ─────────────────────────────────────
@messages.route('/messages/<int:exchange_id>', methods=['GET', 'POST'])
@login_required
def conversation(exchange_id):
    exchange = Exchange.query.get_or_404(exchange_id)
    req      = exchange.request

    # Only participants can view
    if current_user.user_id not in [req.sender_id, req.receiver_id]:
        flash('Unauthorized.', 'error')
        return redirect(url_for('messages.inbox'))

    other = (
        req.receiver
        if req.sender_id == current_user.user_id
        else req.sender
    )

    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        if not content:
            flash('Message cannot be empty.', 'error')
            return redirect(url_for(
                'messages.conversation', exchange_id=exchange_id
            ))

        new_msg = Message(
            exchange_id=exchange_id,
            sender_id=current_user.user_id,
            receiver_id=other.user_id,
            content=content
        )
        db.session.add(new_msg)
        db.session.commit()
        return redirect(url_for(
            'messages.conversation', exchange_id=exchange_id
        ))

    # Mark all received messages as read
    unread_msgs = Message.query.filter_by(
        exchange_id=exchange_id,
        receiver_id=current_user.user_id,
        is_read=False
    ).all()
    for m in unread_msgs:
        m.is_read = True
    db.session.commit()

    all_messages = Message.query.filter_by(
        exchange_id=exchange_id
    ).order_by(Message.timestamp.asc()).all()

    return render_template(
        'messages/conversation.html',
        exchange=exchange,
        other=other,
        all_messages=all_messages
    )