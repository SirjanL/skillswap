from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import auth
from app import db
from app.models import User
from app.models import UserSkill 


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        name             = request.form.get('name').strip()
        email            = request.form.get('email').strip().lower()
        password         = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))
        
        location = request.form.get('location', '').strip()

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))

        if not location:
            flash('Location is required.', 'error')
            return redirect(url_for('auth.register'))        

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with that email already exists.', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, location=location, role='user')
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email').strip().lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))



@auth.route('/')
@auth.route('/dashboard')
@login_required
def dashboard():
    from app.matching.routes import get_matches

    offered_count = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='offer'
    ).count()
    wanted_count = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='want'
    ).count()
    match_count = len(get_matches(current_user.user_id))

    return render_template(
        'home.html',
        offered_count=offered_count,
        wanted_count=wanted_count,
        match_count=match_count
    )