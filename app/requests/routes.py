from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.requests import requests_bp
from app import db
from app.models import User, UserSkill, Request, Exchange, Notification
from app.matching.routes import get_matches
from flask import jsonify


@requests_bp.route('/request/send/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_request(receiver_id):
    if receiver_id == current_user.user_id:
        flash('You cannot send a request to yourself.', 'error')
        return redirect(url_for('matching.discover'))

    receiver = User.query.get_or_404(receiver_id)

    matches = get_matches(current_user.user_id)
    match_info = next(
        (m for m in matches if m['user'].user_id == receiver_id), None
    )

    if not match_info:
        flash('You can only send requests to matched users.', 'error')
        return redirect(url_for('matching.discover'))

    if request.method == 'POST':
        offered_skill_id   = request.form.get('offered_skill_id', type=int)
        requested_skill_id = request.form.get('requested_skill_id', type=int)
        message            = request.form.get('message', '').strip()

        if not offered_skill_id or not requested_skill_id:
            flash('Please select both skills.', 'error')
            return redirect(url_for('requests_bp.send_request', receiver_id=receiver_id))

        existing = Request.query.filter_by(
            sender_id=current_user.user_id,
            receiver_id=receiver_id,
            status='pending'
        ).first()

        if existing:
            flash('You already have a pending request with this user.', 'error')
            return redirect(url_for('matching.user_detail', user_id=receiver_id))

        new_request = Request(
            sender_id=current_user.user_id,
            receiver_id=receiver_id,
            offered_skill_id=offered_skill_id,
            requested_skill_id=requested_skill_id,
            message=message,
            status='pending'
        )
        db.session.add(new_request)
        db.session.flush()  # get request_id before commit

        notification = Notification(
            user_id=receiver_id,
            request_id=new_request.request_id,
            type='new_request',
            message=f'{current_user.name} sent you a skill exchange request!'
        )
        db.session.add(notification)
        db.session.commit()

        flash(f'Request sent to {receiver.name}!', 'success')
        return redirect(url_for('requests_bp.inbox'))

    return render_template(
        'requests/send_request.html',
        receiver=receiver,
        match_info=match_info
    )


@requests_bp.route('/inbox')
@login_required
def inbox():
    received = Request.query.filter_by(
        receiver_id=current_user.user_id
    ).order_by(Request.created_at.desc()).all()

    sent = Request.query.filter_by(
        sender_id=current_user.user_id
    ).order_by(Request.created_at.desc()).all()

    return render_template('requests/inbox.html', received=received, sent=sent)


@requests_bp.route('/request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def request_detail(request_id):
    req = Request.query.get_or_404(request_id)

    if current_user.user_id not in [req.sender_id, req.receiver_id]:
        flash('Unauthorized.', 'error')
        return redirect(url_for('requests_bp.inbox'))

    if request.method == 'POST':
        action = request.form.get('action')  # 'accept' or 'reject'

        if current_user.user_id != req.receiver_id:
            flash('Only the receiver can respond to this request.', 'error')
            return redirect(url_for('requests_bp.request_detail', request_id=request_id))

        if req.status != 'pending':
            flash('This request has already been responded to.', 'error')
            return redirect(url_for('requests_bp.inbox'))

        if action == 'accept':
            req.status = 'accepted'

            exchange = Exchange(
                request_id=req.request_id,
                status='active'
            )
            db.session.add(exchange)
            db.session.flush()

            notification = Notification(
                user_id=req.sender_id,
                request_id=req.request_id,
                type='accepted',
                message=f'{current_user.name} accepted your skill exchange request!'
            )
            db.session.add(notification)
            db.session.commit()

            flash(f'Request accepted! Your exchange with {req.sender.name} is now active.', 'success')

        elif action == 'reject':
            req.status = 'rejected'

            notification = Notification(
                user_id=req.sender_id,
                request_id=req.request_id,
                type='rejected',
                message=f'{current_user.name} declined your skill exchange request.'
            )
            db.session.add(notification)
            db.session.commit()

            flash('Request declined.', 'success')

        return redirect(url_for('requests_bp.inbox'))

    return render_template('requests/request_detail.html', req=req)


@requests_bp.route('/exchanges')
@login_required
def exchanges():
    active = Request.query.filter(
        Request.status.in_(['accepted', 'rejected']),
        db.or_(
            Request.sender_id == current_user.user_id,
            Request.receiver_id == current_user.user_id
        )
    ).all()

    return render_template('requests/exchanges.html', exchanges=active)


@requests_bp.route('/exchange/complete/<int:exchange_id>')
@login_required
def complete_exchange(exchange_id):
    exchange = Exchange.query.get_or_404(exchange_id)
    req      = exchange.request

    if current_user.user_id not in [req.sender_id, req.receiver_id]:
        flash('Unauthorized.', 'error')
        return redirect(url_for('requests_bp.exchanges'))

    exchange.status = 'completed'
    db.session.commit()

    flash('Exchange marked as completed! Don\'t forget to rate each other.', 'success')
    return redirect(url_for('requests_bp.exchanges'))

@requests_bp.route('/request/cancel/<int:request_id>')
@login_required
def cancel_request(request_id):
    req = Request.query.get_or_404(request_id)

    if current_user.user_id != req.sender_id:
        flash('Only the sender can cancel a request.', 'error')
        return redirect(url_for('requests_bp.inbox'))

    # Can only cancel pending requests
    if req.status != 'pending':
        flash('Only pending requests can be cancelled.', 'error')
        return redirect(url_for('requests_bp.inbox'))

    Notification.query.filter_by(request_id=req.request_id).delete()

    db.session.delete(req)
    db.session.commit()

    flash('Request cancelled successfully.', 'success')
    return redirect(url_for('requests_bp.inbox'))

@requests_bp.route('/exchange/cancel/<int:exchange_id>')
@login_required
def cancel_exchange(exchange_id):
    exchange = Exchange.query.get_or_404(exchange_id)
    req      = exchange.request

    if current_user.user_id not in [req.sender_id, req.receiver_id]:
        flash('Unauthorized.', 'error')
        return redirect(url_for('requests_bp.exchanges'))

    if exchange.status != 'active':
        flash('Only active exchanges can be cancelled.', 'error')
        return redirect(url_for('requests_bp.exchanges'))

    exchange.status = 'cancelled'
    req.status      = 'rejected'

    other_user_id = (
        req.receiver_id
        if current_user.user_id == req.sender_id
        else req.sender_id
    )

    notification = Notification(
        user_id=other_user_id,
        request_id=req.request_id,
        type='rejected',
        message=f'{current_user.name} cancelled your skill exchange.'
    )
    db.session.add(notification)
    db.session.commit()

    flash('Exchange cancelled successfully.', 'success')
    return redirect(url_for('requests_bp.exchanges'))

@requests_bp.route('/inbox/poll')
@login_required
def poll_inbox():
    pending_received = Request.query.filter_by(
        receiver_id=current_user.user_id,
        status='pending'
    ).count()

    return jsonify({'pending_count': pending_received})

@requests_bp.route('/exchanges/poll')
@login_required
def poll_exchanges():
    active_count = Request.query.filter(
        Request.status == 'accepted',
        db.or_(
            Request.sender_id == current_user.user_id,
            Request.receiver_id == current_user.user_id
        )
    ).count()

    return jsonify({'active_count': active_count})