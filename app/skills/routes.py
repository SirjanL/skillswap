from flask import render_template, request
from flask_login import login_required, current_user
from app.skills import skills
from app.models import Skill, UserSkill, User
from app.profile.routes import SKILL_CATEGORIES


# ── BROWSE ALL SKILLS ─────────────────────────────────────
@skills.route('/skills')
@login_required
def browse():
    search   = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    query = Skill.query

    if search:
        query = query.filter(
            Skill.skill_name.ilike(f'%{search}%')
        )
    if category:
        query = query.filter_by(category=category)

    all_skills = query.order_by(Skill.category, Skill.skill_name).all()

    my_skill_ids = {
        us.skill_id for us in
        UserSkill.query.filter_by(user_id=current_user.user_id).all()
    }

    return render_template(
        'skills/browse.html',
        all_skills=all_skills,
        categories=SKILL_CATEGORIES,
        my_skill_ids=my_skill_ids,
        search=search,
        category=category
    )


# ── SKILL DETAIL ──────────────────────────────────────────
@skills.route('/skills/<int:skill_id>')
@login_required
def skill_detail(skill_id):
    skill = Skill.query.get_or_404(skill_id)

    # Users offering this skill
    offering = UserSkill.query.filter_by(
        skill_id=skill_id, type='offer'
    ).all()

    # Users wanting this skill
    wanting = UserSkill.query.filter_by(
        skill_id=skill_id, type='want'
    ).all()

    # Check if current user has this skill
    my_user_skill = UserSkill.query.filter_by(
        user_id=current_user.user_id,
        skill_id=skill_id
    ).first()

    return render_template(
        'skills/skill_detail.html',
        skill=skill,
        offering=offering,
        wanting=wanting,
        my_user_skill=my_user_skill
    )