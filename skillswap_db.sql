-- ============================================================
-- SkillSwap: A Local Skill Exchange Platform
-- Database Schema (PostgreSQL)
-- Author: Sirjan Lamichhane | Enrollment: 239150610
-- BCA 6th Semester | IGNOU | BCSP-064
-- ============================================================


-- ── 1. USERS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id    SERIAL PRIMARY KEY,
    name       VARCHAR(100)        NOT NULL,
    email      VARCHAR(120) UNIQUE NOT NULL,
    password   VARCHAR(256)        NOT NULL,
    bio        TEXT                DEFAULT '',
    location   VARCHAR(100)        DEFAULT '',
    is_active  BOOLEAN             DEFAULT TRUE,
    created_at TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);


-- ── 2. SKILLS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS skills (
    skill_id    SERIAL PRIMARY KEY,
    skill_name  VARCHAR(100) UNIQUE NOT NULL,
    description TEXT                DEFAULT '',
    category    VARCHAR(100)        DEFAULT 'General'
);


-- ── 3. USER_SKILLS ────────────────────────────────────────
-- Junction table linking users to skills
-- type  : 'offer' = user can teach this skill
--         'want'  = user wants to learn this skill
-- level : beginner / intermediate / advanced
CREATE TABLE IF NOT EXISTS user_skills (
    id       SERIAL PRIMARY KEY,
    user_id  INTEGER NOT NULL REFERENCES users(user_id)   ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    type     VARCHAR(10)  NOT NULL CHECK (type IN ('offer', 'want')),
    level    VARCHAR(20)  DEFAULT 'beginner'
                          CHECK (level IN ('beginner', 'intermediate', 'advanced'))
);


-- ── 4. REQUESTS ───────────────────────────────────────────
-- A skill exchange request sent from one user to another
-- status: pending / accepted / rejected
CREATE TABLE IF NOT EXISTS requests (
    request_id          SERIAL PRIMARY KEY,
    sender_id           INTEGER NOT NULL REFERENCES users(user_id)  ON DELETE CASCADE,
    receiver_id         INTEGER NOT NULL REFERENCES users(user_id)  ON DELETE CASCADE,
    offered_skill_id    INTEGER NOT NULL REFERENCES skills(skill_id),
    requested_skill_id  INTEGER NOT NULL REFERENCES skills(skill_id),
    message             TEXT    DEFAULT '',
    status              VARCHAR(20) DEFAULT 'pending'
                                    CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ── 5. EXCHANGES ──────────────────────────────────────────
-- Created automatically when a request is accepted
-- status: active / completed / cancelled
CREATE TABLE IF NOT EXISTS exchanges (
    exchange_id SERIAL PRIMARY KEY,
    request_id  INTEGER NOT NULL REFERENCES requests(request_id) ON DELETE CASCADE,
    start_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date    TIMESTAMP,
    status      VARCHAR(20) DEFAULT 'active'
                            CHECK (status IN ('active', 'completed', 'cancelled'))
);


-- ── 6. RATINGS ────────────────────────────────────────────
-- Post-exchange ratings submitted by participants
-- rating: integer between 1 and 5
CREATE TABLE IF NOT EXISTS ratings (
    rating_id      SERIAL PRIMARY KEY,
    exchange_id    INTEGER NOT NULL REFERENCES exchanges(exchange_id) ON DELETE CASCADE,
    rater_id       INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    rated_user_id  INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    rating         INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback       TEXT    DEFAULT ''
);


-- ── 7. NOTIFICATIONS ──────────────────────────────────────
-- Platform notifications triggered by request/exchange events
-- type: new_request / accepted / rejected
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id)     ON DELETE CASCADE,
    request_id      INTEGER          REFERENCES requests(request_id) ON DELETE SET NULL,
    type            VARCHAR(50) NOT NULL,
    is_read         BOOLEAN     DEFAULT FALSE,
    message         TEXT        DEFAULT '',
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);


-- ── 8. MESSAGES ───────────────────────────────────────────
-- Direct messages between users within an active exchange
CREATE TABLE IF NOT EXISTS messages (
    message_id  SERIAL PRIMARY KEY,
    exchange_id INTEGER NOT NULL REFERENCES exchanges(exchange_id) ON DELETE CASCADE,
    sender_id   INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    content     TEXT    NOT NULL,
    is_read     BOOLEAN   DEFAULT FALSE,
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- INDEXES for performance on frequently queried columns
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_user_skills_user    ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill   ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_requests_sender     ON requests(sender_id);
CREATE INDEX IF NOT EXISTS idx_requests_receiver   ON requests(receiver_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user  ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_exchange   ON messages(exchange_id);


-- ============================================================
-- SAMPLE DATA for demonstration purposes
-- ============================================================

-- Sample skills
INSERT INTO skills (skill_name, description, category) VALUES
    ('Python',      'Programming in Python',         'Programming'),
    ('Guitar',      'Acoustic and electric guitar',  'Music'),
    ('Photoshop',   'Adobe Photoshop editing',        'Design'),
    ('English',     'English language tutoring',      'Language'),
    ('Mathematics', 'High school and college math',   'Education'),
    ('Cooking',     'Basic to advanced cooking',      'Lifestyle')
ON CONFLICT (skill_name) DO NOTHING;