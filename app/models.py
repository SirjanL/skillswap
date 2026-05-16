from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# Required by Flask-Login to load a user from the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── 1. USER ──────────────────────────────────────────────
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id    = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    bio        = db.Column(db.Text, default='')
    location   = db.Column(db.String(100), default='')
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user_skills        = db.relationship('UserSkill', backref='user', lazy=True)
    sent_requests      = db.relationship('Request', foreign_keys='Request.sender_id',   backref='sender',   lazy=True)
    received_requests  = db.relationship('Request', foreign_keys='Request.receiver_id', backref='receiver', lazy=True)
    notifications      = db.relationship('Notification', backref='user', lazy=True)
    sent_messages      = db.relationship('Message', foreign_keys='Message.sender_id',   backref='sender',   lazy=True)
    received_messages  = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

    # Flask-Login needs this to be 'user_id' not default 'id'
    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'<User {self.name}>'


# ── 2. SKILL ─────────────────────────────────────────────
class Skill(db.Model):
    __tablename__ = 'skills'

    skill_id    = db.Column(db.Integer, primary_key=True)
    skill_name  = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    category    = db.Column(db.String(100), default='General')

    user_skills = db.relationship('UserSkill', backref='skill', lazy=True)

    def __repr__(self):
        return f'<Skill {self.skill_name}>'


# ── 3. USER_SKILLS (junction table) ──────────────────────
class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.user_id'),  nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.skill_id'), nullable=False)
    type     = db.Column(db.String(10), nullable=False)   # 'offer' or 'want'
    level    = db.Column(db.String(20), default='beginner')  # beginner / intermediate / advanced

    def __repr__(self):
        return f'<UserSkill user={self.user_id} skill={self.skill_id} type={self.type}>'


# ── 4. REQUEST ────────────────────────────────────────────
class Request(db.Model):
    __tablename__ = 'requests'

    request_id        = db.Column(db.Integer, primary_key=True)
    sender_id         = db.Column(db.Integer, db.ForeignKey('users.user_id'),  nullable=False)
    receiver_id       = db.Column(db.Integer, db.ForeignKey('users.user_id'),  nullable=False)
    offered_skill_id  = db.Column(db.Integer, db.ForeignKey('skills.skill_id'), nullable=False)
    requested_skill_id= db.Column(db.Integer, db.ForeignKey('skills.skill_id'), nullable=False)
    message           = db.Column(db.Text, default='')
    status            = db.Column(db.String(20), default='pending')  # pending / accepted / rejected
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    exchange      = db.relationship('Exchange', backref='request', uselist=False, lazy=True)
    notifications = db.relationship('Notification', backref='request', lazy=True)

    offered_skill   = db.relationship('Skill', foreign_keys=[offered_skill_id])
    requested_skill = db.relationship('Skill', foreign_keys=[requested_skill_id])

    def __repr__(self):
        return f'<Request {self.request_id} status={self.status}>'


# ── 5. EXCHANGE ───────────────────────────────────────────
class Exchange(db.Model):
    __tablename__ = 'exchanges'

    exchange_id = db.Column(db.Integer, primary_key=True)
    request_id  = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    start_date  = db.Column(db.DateTime, default=datetime.utcnow)
    end_date    = db.Column(db.DateTime, nullable=True)
    status      = db.Column(db.String(20), default='active')  # active / completed / cancelled

    ratings  = db.relationship('Rating',       backref='exchange', lazy=True)
    messages = db.relationship('Message',      backref='exchange', lazy=True)

    def __repr__(self):
        return f'<Exchange {self.exchange_id} status={self.status}>'


# ── 6. RATING ─────────────────────────────────────────────
class Rating(db.Model):
    __tablename__ = 'ratings'

    rating_id      = db.Column(db.Integer, primary_key=True)
    exchange_id    = db.Column(db.Integer, db.ForeignKey('exchanges.exchange_id'), nullable=False)
    rater_id       = db.Column(db.Integer, db.ForeignKey('users.user_id'),         nullable=False)
    rated_user_id  = db.Column(db.Integer, db.ForeignKey('users.user_id'),         nullable=False)
    rating         = db.Column(db.Integer, nullable=False)
    feedback       = db.Column(db.Text, default='')

    rater = db.relationship('User', foreign_keys=[rater_id])   # ← ADD THIS

    def __repr__(self):
        return f'<Rating {self.rating_id} rating={self.rating}>'


# ── 7. NOTIFICATION ───────────────────────────────────────
class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.user_id'),    nullable=False)
    request_id      = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=True)
    type            = db.Column(db.String(50), nullable=False)  # e.g. 'new_request', 'accepted'
    is_read         = db.Column(db.Boolean, default=False)
    message         = db.Column(db.Text, default='')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.notification_id} type={self.type}>'


# ── 8. MESSAGE ────────────────────────────────────────────
class Message(db.Model):
    __tablename__ = 'messages'

    message_id  = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchanges.exchange_id'), nullable=False)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.user_id'),         nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),         nullable=False)
    content     = db.Column(db.Text, nullable=False)
    is_read     = db.Column(db.Boolean, default=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.message_id}>'
    
