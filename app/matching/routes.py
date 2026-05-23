from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.matching import matching
from app.models import User, UserSkill, Skill


def get_matches(current_user_id):
    my_offered_skill_ids = {
        us.skill_id for us in
        UserSkill.query.filter_by(user_id=current_user_id, type='offer').all()
    }
    my_wanted_skill_ids = {
        us.skill_id for us in
        UserSkill.query.filter_by(user_id=current_user_id, type='want').all()
    }

    if not my_offered_skill_ids or not my_wanted_skill_ids:
        return []

    matches = []

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

        they_can_teach_me = my_wanted_skill_ids & their_offered_skill_ids

        i_can_teach_them = my_offered_skill_ids & their_wanted_skill_ids

        if they_can_teach_me and i_can_teach_them:

            teach_me_skills = Skill.query.filter(
                Skill.skill_id.in_(they_can_teach_me)
            ).all()
            teach_them_skills = Skill.query.filter(
                Skill.skill_id.in_(i_can_teach_them)
            ).all()

            score = len(they_can_teach_me) + len(i_can_teach_them)

            matches.append({
                'user': user,
                'they_can_teach_me': teach_me_skills,
                'i_can_teach_them':  teach_them_skills,
                'score': score
            })

    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches


@matching.route('/discover')
@login_required
def discover():
    search = request.args.get('q', '').strip()
    matches = get_matches(current_user.user_id)

    if search:
        matches = [
            m for m in matches
            if search.lower() in m['user'].name.lower()
            or search.lower() in m['user'].location.lower()
            or any(search.lower() in s.skill_name.lower()
                   for s in m['they_can_teach_me'])
            or any(search.lower() in s.skill_name.lower()
                   for s in m['i_can_teach_them'])
        ]

    return render_template(
        'matching/discover.html',
        matches=matches,
        search=search
    )

@matching.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    if user_id == current_user.user_id:
        return redirect(url_for('profile.view_profile'))

    from app.models import Rating
    user = User.query.get_or_404(user_id)

    offered_skills = UserSkill.query.filter_by(
        user_id=user_id, type='offer'
    ).all()
    wanted_skills = UserSkill.query.filter_by(
        user_id=user_id, type='want'
    ).all()

    all_ratings = Rating.query.filter_by(rated_user_id=user_id).all()
    avg_rating  = (
        round(sum(r.rating for r in all_ratings) / len(all_ratings), 1)
        if all_ratings else None
    )

    matches    = get_matches(current_user.user_id)
    match_info = next(
        (m for m in matches if m['user'].user_id == user_id), None
    )

    return render_template(
        'matching/user_detail.html',
        user=user,
        offered_skills=offered_skills,
        wanted_skills=wanted_skills,
        match_info=match_info,
        all_ratings=all_ratings,
        avg_rating=avg_rating
    )