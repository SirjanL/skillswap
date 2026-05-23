from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.profile import profile
from app import db
from app.models import User, Skill, UserSkill


@profile.route('/profile')
@login_required
def view_profile():
    from app.models import Rating
    offered_skills = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='offer'
    ).all()
    wanted_skills = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='want'
    ).all()
    all_ratings = Rating.query.filter_by(
        rated_user_id=current_user.user_id
    ).all()
    avg_rating = (
        round(sum(r.rating for r in all_ratings) / len(all_ratings), 1)
        if all_ratings else None
    )
    return render_template(
        'profile/profile.html',
        user=current_user,
        offered_skills=offered_skills,
        wanted_skills=wanted_skills,
        all_ratings=all_ratings,
        avg_rating=avg_rating
    )


@profile.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name     = request.form.get('name').strip()
        bio      = request.form.get('bio').strip()
        location = request.form.get('location').strip()

        if not name:
            flash('Name cannot be empty.', 'error')
            return redirect(url_for('profile.edit_profile'))
        if not location:
            flash('Location is required.', 'error')
            return redirect(url_for('profile.edit_profile'))
        
        current_user.name     = name
        current_user.bio      = bio
        current_user.location = location
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))

    return render_template('profile/edit_profile.html', user=current_user)


SKILL_CATEGORIES = {
    'Tech & Development': [
        'Programming', 'Web Development', 'Mobile Development', 
        'Cloud Computing', 'DevOps', 'Database', 'Cybersecurity'
    ],
    'Data & AI': [
        'Data Science', 'Machine Learning', 'Artificial Intelligence'
    ],
    'Design & Visual Arts': [
        'UI/UX Design', 'Graphic Design', 'Video Editing', 'Photography', 
        'Animation', '3D Modeling', 'Drawing', 'Painting', 'Sculpting', 'Calligraphy'
    ],
    'Music & Audio': [
        'Music Production', 'Guitar', 'Piano', 'Drums', 'Singing', 'Music Theory'
    ],
    'Writing & Languages': [
        'Creative Writing', 'Blogging', 'Copywriting', 'Translation', 
        'English', 'Nepali', 'Hindi', 'French', 'Spanish', 'Japanese', 'Chinese'
    ],
    'Academics & Sciences': [
        'Mathematics', 'Physics', 'Chemistry', 'Biology', 'History', 'Geography'
    ],
    'Lifestyle & Wellness': [
        'Cooking', 'Baking', 'Fitness', 'Yoga', 'Meditation'
    ],
    'Business & Professional': [
        'Public Speaking', 'Leadership', 'Finance', 'Accounting'
    ]
}


@profile.route('/profile/skills', methods=['GET', 'POST'])
@login_required
def manage_skills():
    if request.method == 'POST':
        skill_name = request.form.get('skill_name').strip().title()
        category   = request.form.get('category').strip()
        skill_type = request.form.get('skill_type')
        level      = request.form.get('level')

        if not skill_name or skill_type not in ['offer', 'want']:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('profile.manage_skills'))

        if category not in SKILL_CATEGORIES:
            flash('Please select a valid category.', 'error')
            return redirect(url_for('profile.manage_skills'))

        skill = Skill.query.filter_by(skill_name=skill_name).first()
        if not skill:
            skill = Skill(skill_name=skill_name, category=category)
            db.session.add(skill)
            db.session.flush()

        existing = UserSkill.query.filter_by(
            user_id=current_user.user_id,
            skill_id=skill.skill_id,
            type=skill_type
        ).first()

        if existing:
            flash(f'You already added "{skill_name}" as a skill you {skill_type}.', 'error')
            return redirect(url_for('profile.manage_skills'))

        user_skill = UserSkill(
            user_id=current_user.user_id,
            skill_id=skill.skill_id,
            type=skill_type,
            level=level
        )
        db.session.add(user_skill)
        db.session.commit()

        flash(f'"{skill_name}" added to your {skill_type} skills!', 'success')
        return redirect(url_for('profile.manage_skills'))

    offered_skills = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='offer'
    ).all()
    wanted_skills = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='want'
    ).all()

    return render_template(
        'profile/manage_skills.html',
        offered_skills=offered_skills,
        wanted_skills=wanted_skills,
        categories=SKILL_CATEGORIES
    )


@profile.route('/profile/skills/delete/<int:user_skill_id>')
@login_required
def delete_skill(user_skill_id):
    user_skill = UserSkill.query.get_or_404(user_skill_id)

    if user_skill.user_id != current_user.user_id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('profile.manage_skills'))

    db.session.delete(user_skill)
    db.session.commit()
    flash('Skill removed.', 'success')
    return redirect(url_for('profile.manage_skills'))

@profile.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.user_id

    try:
        from app.models import Notification, Message, Rating, Exchange, Request, UserSkill

        # Logout first before deleting
        from flask_login import logout_user
        logout_user()

        # Delete notifications
        Notification.query.filter_by(user_id=user_id).delete()

        # Delete messages
        Message.query.filter(
            db.or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).delete()

        # Delete ratings
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
                Message.query.filter_by(
                    exchange_id=req.exchange.exchange_id
                ).delete()
                Rating.query.filter_by(
                    exchange_id=req.exchange.exchange_id
                ).delete()
                db.session.delete(req.exchange)
            Notification.query.filter_by(
                request_id=req.request_id
            ).delete()
            db.session.delete(req)

        UserSkill.query.filter_by(user_id=user_id).delete()

        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()

        flash('Your account has been permanently deleted.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting account: {str(e)}', 'error')
        return redirect(url_for('profile.view_profile'))

    return redirect(url_for('auth.register'))

@profile.route('/profile/skills/edit/<int:user_skill_id>', methods=['GET', 'POST'])
@login_required
def edit_skill(user_skill_id):
    user_skill = UserSkill.query.get_or_404(user_skill_id)

    if user_skill.user_id != current_user.user_id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('profile.manage_skills'))

    if request.method == 'POST':
        new_level = request.form.get('level')
        new_type  = request.form.get('skill_type')

        if new_type not in ['offer', 'want']:
            flash('Invalid skill type.', 'error')
            return redirect(url_for('profile.edit_skill', user_skill_id=user_skill_id))

        # Check for duplicate if type is being changed
        if new_type != user_skill.type:
            existing = UserSkill.query.filter_by(
                user_id=current_user.user_id,
                skill_id=user_skill.skill_id,
                type=new_type
            ).first()
            if existing:
                flash(
                    f'You already have '
                    f'"{user_skill.skill.skill_name}" as a '
                    f'{new_type} skill.', 'error'
                )
                return redirect(
                    url_for('profile.edit_skill', user_skill_id=user_skill_id)
                )

        user_skill.level = new_level
        user_skill.type  = new_type
        db.session.commit()

        flash(f'"{user_skill.skill.skill_name}" updated successfully!', 'success')
        return redirect(url_for('profile.manage_skills'))

    return render_template('profile/edit_skill.html', user_skill=user_skill)