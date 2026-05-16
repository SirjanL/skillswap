from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.profile import profile
from app import db
from app.models import User, Skill, UserSkill


# ── VIEW PROFILE ──────────────────────────────────────────
@profile.route('/profile')
@login_required
def view_profile():
    offered_skills = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='offer'
    ).all()
    wanted_skills = UserSkill.query.filter_by(
        user_id=current_user.user_id, type='want'
    ).all()
    return render_template(
        'profile/profile.html',
        user=current_user,
        offered_skills=offered_skills,
        wanted_skills=wanted_skills
    )


# ── EDIT PROFILE ──────────────────────────────────────────
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

        current_user.name     = name
        current_user.bio      = bio
        current_user.location = location
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))

    return render_template('profile/edit_profile.html', user=current_user)


# ── MANAGE SKILLS ─────────────────────────────────────────
@profile.route('/profile/skills', methods=['GET', 'POST'])
@login_required
def manage_skills():
    if request.method == 'POST':
        skill_name = request.form.get('skill_name').strip().title()
        category   = request.form.get('category').strip().title()
        skill_type = request.form.get('skill_type')   # 'offer' or 'want'
        level      = request.form.get('level')

        if not skill_name or skill_type not in ['offer', 'want']:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('profile.manage_skills'))

        # Get skill or create it if it doesn't exist yet
        skill = Skill.query.filter_by(skill_name=skill_name).first()
        if not skill:
            skill = Skill(skill_name=skill_name, category=category)
            db.session.add(skill)
            db.session.flush()  # get skill_id before commit

        # Check for duplicate
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
        wanted_skills=wanted_skills
    )


# ── DELETE A SKILL ────────────────────────────────────────
@profile.route('/profile/skills/delete/<int:user_skill_id>')
@login_required
def delete_skill(user_skill_id):
    user_skill = UserSkill.query.get_or_404(user_skill_id)

    # Make sure users can only delete their own skills
    if user_skill.user_id != current_user.user_id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('profile.manage_skills'))

    db.session.delete(user_skill)
    db.session.commit()
    flash('Skill removed.', 'success')
    return redirect(url_for('profile.manage_skills'))