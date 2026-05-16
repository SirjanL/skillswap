from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.matching import matching
from app.models import User, UserSkill, Skill


# ── HELPER: core matching algorithm ──────────────────────
def get_matches(current_user_id):
    """
    Find users who:
      - offer at least one skill that I want
      - AND want at least one skill that I offer
    Returns a list of dicts with match info.
    """

    # Get current user's offered and wanted skill IDs
    my_offered_skill_ids = {
        us.skill_id for us in
        UserSkill.query.filter_by(user_id=current_user_id, type='offer').all()
    }
    my_wanted_skill_ids = {
        us.skill_id for us in
        UserSkill.query.filter_by(user_id=current_user_id, type='want').all()
    }

    # Can't match if user hasn't added any skills
    if not my_offered_skill_ids or not my_wanted_skill_ids:
        return []

    matches = []

    # Get all other users
    other_users = User.query.filter(
        User.user_id != current_user_id,
        User.is_active == True
    ).all()

    for user in other_users:
        their_offered_skill_ids = {
            us.skill_id for us in
            UserSkill.query.filter_by(user_id=user.user_id, type='offer').all()
        }
        their_wanted_skill_ids = {
            us.skill_id for us in
            UserSkill.query.filter_by(user_id=user.user_id, type='want').all()
        }

        # Skills they offer that I want
        they_can_teach_me = my_wanted_skill_ids & their_offered_skill_ids

        # Skills I offer that they want
        i_can_teach_them = my_offered_skill_ids & their_wanted_skill_ids

        # Only a match if BOTH sides have something to exchange
        if they_can_teach_me and i_can_teach_them:

            # Get full skill objects for display
            teach_me_skills = Skill.query.filter(
                Skill.skill_id.in_(they_can_teach_me)
            ).all()
            teach_them_skills = Skill.query.filter(
                Skill.skill_id.in_(i_can_teach_them)
            ).all()

            # Match score = total overlapping skills (more = better match)
            score = len(they_can_teach_me) + len(i_can_teach_them)

            matches.append({
                'user': user,
                'they_can_teach_me': teach_me_skills,
                'i_can_teach_them':  teach_them_skills,
                'score': score
            })

    # Sort by best match first
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches


# ── DISCOVER PAGE ─────────────────────────────────────────
@matching.route('/discover')
@login_required
def discover():
    matches = get_matches(current_user.user_id)
    return render_template('matching/discover.html', matches=matches)


# ── VIEW ANOTHER USER'S PROFILE ───────────────────────────
@matching.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    if user_id == current_user.user_id:
        return redirect(url_for('profile.view_profile'))

    user = User.query.get_or_404(user_id)

    offered_skills = UserSkill.query.filter_by(
        user_id=user_id, type='offer'
    ).all()
    wanted_skills = UserSkill.query.filter_by(
        user_id=user_id, type='want'
    ).all()

    # Check if there's a mutual match with current user
    matches = get_matches(current_user.user_id)
    match_info = next(
        (m for m in matches if m['user'].user_id == user_id), None
    )

    return render_template(
        'matching/user_detail.html',
        user=user,
        offered_skills=offered_skills,
        wanted_skills=wanted_skills,
        match_info=match_info
    )