from flask import render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.admin import admin
from app import db
from app.models import Admin, User, Skill, UserSkill, Request, Exchange, Rating, Message
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as admin.', 'error')
            return redirect(url_for('admin.login'))

        # Verify admin still exists in database
        from app.models import Admin
        admin_user = Admin.query.filter_by(
            email=session.get('admin_email')
        ).first()

        if not admin_user:
            session.clear()
            flash('Admin account no longer exists.', 'error')
            return redirect(url_for('admin.login'))

        return f(*args, **kwargs)
    return decorated


@admin.route('/setup', methods=['GET', 'POST'])
def setup():
    if Admin.query.first():
        flash('Admin already exists. Please log in.', 'error')
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        name     = request.form.get('name').strip()
        email    = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm  = request.form.get('confirm_password')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('admin.setup'))

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('admin.setup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('admin.setup'))

        new_admin = Admin(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin account created! Please log in.', 'success')
        return redirect(url_for('admin.login'))

    return render_template('admin/login.html', setup_mode=True)


@admin.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email').strip().lower()
        password = request.form.get('password')

        admin_user = Admin.query.filter_by(email=email).first()

        if not admin_user or not check_password_hash(admin_user.password, password):
            flash('Invalid credentials.', 'error')
            return redirect(url_for('admin.login'))

        session['admin_logged_in'] = True
        session['admin_name']      = admin_user.name
        session['admin_email']     = admin_user.email
        flash(f'Welcome, {admin_user.name}!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html', setup_mode=False)


@admin.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_name', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin.login'))


@admin.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total_users':     User.query.count(),
        'active_users':    User.query.filter_by(is_active=True).count(),
        'total_skills':    Skill.query.count(),
        'total_exchanges': Exchange.query.count(),
        'active_exchanges':   Exchange.query.filter_by(status='active').count(),
        'completed_exchanges': Exchange.query.filter_by(status='completed').count(),
        'pending_requests':   Request.query.filter_by(status='pending').count(),
        'total_messages':  Message.query.count(),
        'total_ratings':   Rating.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)


@admin.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin.route('/users/toggle/<int:user_id>')
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'{user.name} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    try:
        from app.models import Notification, Message, Rating, Exchange, Request, UserSkill

        Notification.query.filter(
            db.or_(Notification.user_id == user_id)
        ).delete()

        Message.query.filter(
            db.or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).delete()

        Rating.query.filter(
            db.or_(
                Rating.rater_id == user_id,
                Rating.rated_user_id == user_id
            )
        ).delete()

        user_requests = Request.query.filter(
            db.or_(
                Request.sender_id == user_id,
                Request.receiver_id == user_id
            )
        ).all()

        for req in user_requests:
            if req.exchange:
                Message.query.filter_by(exchange_id=req.exchange.exchange_id).delete()
                Rating.query.filter_by(exchange_id=req.exchange.exchange_id).delete()
                db.session.delete(req.exchange)
            Notification.query.filter_by(request_id=req.request_id).delete()
            db.session.delete(req)

        UserSkill.query.filter_by(user_id=user_id).delete()

        db.session.delete(user)
        db.session.commit()
        flash(f'User deleted successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')

    return redirect(url_for('admin.users'))


@admin.route('/skills')
@admin_required
def skills():
    all_skills = Skill.query.order_by(Skill.category).all()
    return render_template('admin/skills.html', skills=all_skills)


@admin.route('/skills/delete/<int:skill_id>')
@admin_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)

    try:
        UserSkill.query.filter_by(skill_id=skill_id).delete()

        Request.query.filter_by(offered_skill_id=skill_id).update(
            {'offered_skill_id': None}
        )
        Request.query.filter_by(requested_skill_id=skill_id).update(
            {'requested_skill_id': None}
        )

        db.session.delete(skill)
        db.session.commit()
        flash(f'Skill "{skill.skill_name}" deleted.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting skill: {str(e)}', 'error')

    return redirect(url_for('admin.skills'))


@admin.route('/exchanges')
@admin_required
def exchanges():
    all_exchanges = Exchange.query.order_by(
        Exchange.start_date.desc()
    ).all()
    return render_template('admin/exchanges.html', exchanges=all_exchanges)