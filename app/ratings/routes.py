from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.ratings import ratings
from app import db
from app.models import Exchange, Rating, Request


# ── RATE A USER ───────────────────────────────────────────
@ratings.route('/rate/<int:exchange_id>', methods=['GET', 'POST'])
@login_required
def rate(exchange_id):
    exchange = Exchange.query.get_or_404(exchange_id)
    req      = exchange.request

    # Only participants can rate
    if current_user.user_id not in [req.sender_id, req.receiver_id]:
        flash('Unauthorized.', 'error')
        return redirect(url_for('requests_bp.exchanges'))

    # Only allow rating completed exchanges
    if exchange.status != 'completed':
        flash('You can only rate completed exchanges.', 'error')
        return redirect(url_for('requests_bp.exchanges'))

    # Who is the other person?
    rated_user_id = (
        req.receiver_id
        if current_user.user_id == req.sender_id
        else req.sender_id
    )

    # Check if already rated
    existing = Rating.query.filter_by(
        exchange_id=exchange_id,
        rater_id=current_user.user_id
    ).first()

    if existing:
        flash('You have already rated this exchange.', 'error')
        return redirect(url_for('requests_bp.exchanges'))

    if request.method == 'POST':
        rating_value = request.form.get('rating', type=int)
        feedback     = request.form.get('feedback', '').strip()

        if not rating_value or rating_value not in range(1, 6):
            flash('Please select a rating between 1 and 5.', 'error')
            return redirect(url_for('ratings.rate', exchange_id=exchange_id))

        new_rating = Rating(
            exchange_id=exchange_id,
            rater_id=current_user.user_id,
            rated_user_id=rated_user_id,
            rating=rating_value,
            feedback=feedback
        )
        db.session.add(new_rating)
        db.session.commit()

        flash('Rating submitted! Thanks for your feedback.', 'success')
        return redirect(url_for('requests_bp.exchanges'))

    # Get the other user's info for display
    from app.models import User
    rated_user = User.query.get(rated_user_id)

    return render_template(
        'ratings/rate.html',
        exchange=exchange,
        rated_user=rated_user
    )


# ── VIEW RATINGS ON PROFILE ───────────────────────────────
@ratings.route('/profile/ratings/<int:user_id>')
@login_required
def user_ratings(user_id):
    from app.models import User
    user        = User.query.get_or_404(user_id)
    all_ratings = Rating.query.filter_by(rated_user_id=user_id).all()
    avg = (
        round(sum(r.rating for r in all_ratings) / len(all_ratings), 1)
        if all_ratings else None
    )
    return render_template(
        'ratings/user_ratings.html',
        user=user,
        all_ratings=all_ratings,
        avg=avg
    )