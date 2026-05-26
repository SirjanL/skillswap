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


CREATE TABLE IF NOT EXISTS skills (
    skill_id    SERIAL PRIMARY KEY,
    skill_name  VARCHAR(100) UNIQUE NOT NULL,
    description TEXT                DEFAULT '',
    category    VARCHAR(100)        DEFAULT 'General'
);


CREATE TABLE IF NOT EXISTS user_skills (
    id       SERIAL PRIMARY KEY,
    user_id  INTEGER NOT NULL REFERENCES users(user_id)   ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    type     VARCHAR(10)  NOT NULL CHECK (type IN ('offer', 'want')),
    level    VARCHAR(20)  DEFAULT 'beginner'
                          CHECK (level IN ('beginner', 'intermediate', 'advanced'))
);


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


CREATE TABLE IF NOT EXISTS exchanges (
    exchange_id SERIAL PRIMARY KEY,
    request_id  INTEGER NOT NULL REFERENCES requests(request_id) ON DELETE CASCADE,
    start_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date    TIMESTAMP,
    status      VARCHAR(20) DEFAULT 'active'
                            CHECK (status IN ('active', 'completed', 'cancelled'))
);


CREATE TABLE IF NOT EXISTS ratings (
    rating_id      SERIAL PRIMARY KEY,
    exchange_id    INTEGER NOT NULL REFERENCES exchanges(exchange_id) ON DELETE CASCADE,
    rater_id       INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    rated_user_id  INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    rating         INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback       TEXT    DEFAULT ''
);


CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id)     ON DELETE CASCADE,
    request_id      INTEGER          REFERENCES requests(request_id) ON DELETE SET NULL,
    type            VARCHAR(50) NOT NULL,
    is_read         BOOLEAN     DEFAULT FALSE,
    message         TEXT        DEFAULT '',
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS messages (
    message_id  SERIAL PRIMARY KEY,
    exchange_id INTEGER NOT NULL REFERENCES exchanges(exchange_id) ON DELETE CASCADE,
    sender_id   INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE,
    content     TEXT    NOT NULL,
    is_read     BOOLEAN   DEFAULT FALSE,
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_user_skills_user    ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill   ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_requests_sender     ON requests(sender_id);
CREATE INDEX IF NOT EXISTS idx_requests_receiver   ON requests(receiver_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user  ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_exchange   ON messages(exchange_id);


INSERT INTO skills (skill_name, description, category) VALUES
    ('Python',      'Programming in Python',         'Programming'),
    ('Guitar',      'Acoustic and electric guitar',  'Music'),
    ('Photoshop',   'Adobe Photoshop editing',        'Design'),
    ('English',     'English language tutoring',      'Language'),
    ('Mathematics', 'High school and college math',   'Education'),
    ('Cooking',     'Basic to advanced cooking',      'Lifestyle')
ON CONFLICT (skill_name) DO NOTHING;


CREATE TABLE IF NOT EXISTS admins (
    admin_id   SERIAL PRIMARY KEY,
    name       VARCHAR(100)        NOT NULL,
    email      VARCHAR(120) UNIQUE NOT NULL,
    password   VARCHAR(256)        NOT NULL,
    created_at TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE requests ALTER COLUMN offered_skill_id DROP NOT NULL;
ALTER TABLE requests ALTER COLUMN requested_skill_id DROP NOT NULL;


CREATE INDEX IF NOT EXISTS idx_exchanges_status ON exchanges(status);
CREATE INDEX IF NOT EXISTS idx_requests_status  ON requests(status);


-- 20 Demo Users from Nepal
INSERT INTO users (name, email, password, bio, location, is_active, role, created_at) VALUES

('Aarav Sharma', 'aarav.sharma@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Passionate software developer who loves teaching Python and learning music.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '45 days'),

('Priya Thapa', 'priya.thapa@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Graphic designer with 5 years of experience. Love to sketch and paint in free time.', 'Pokhara, Nepal', true, 'user', NOW() - INTERVAL '40 days'),

('Bikash Adhikari', 'bikash.adhikari@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Guitar teacher at a local music school. Looking to learn web development.', 'Lalitpur, Nepal', true, 'user', NOW() - INTERVAL '38 days'),

('Sita Rai', 'sita.rai@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Professional chef specializing in Nepali and Continental cuisine. Want to learn photography.', 'Bhaktapur, Nepal', true, 'user', NOW() - INTERVAL '35 days'),

('Rohan Gurung', 'rohan.gurung@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Freelance photographer covering landscapes and portraits across Nepal.', 'Pokhara, Nepal', true, 'user', NOW() - INTERVAL '32 days'),

('Anita Karki', 'anita.karki@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'English literature graduate. Offer tutoring in English and creative writing.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '30 days'),

('Dipesh Magar', 'dipesh.magar@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Data analyst working at a fintech startup. Interested in learning yoga and fitness.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '28 days'),

('Sunita Bhandari', 'sunita.bhandari@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Certified yoga instructor with 8 years of experience. Want to learn graphic design.', 'Lalitpur, Nepal', true, 'user', NOW() - INTERVAL '26 days'),

('Nabin Shrestha', 'nabin.shrestha@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Mobile app developer specializing in Flutter. Looking to improve my cooking skills.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '24 days'),

('Kamala Tamang', 'kamala.tamang@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Traditional Thanka painter. Interested in learning digital design tools.', 'Bhaktapur, Nepal', true, 'user', NOW() - INTERVAL '22 days'),

('Rajan Poudel', 'rajan.poudel@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Mathematics teacher at a secondary school. Want to learn programming and music production.', 'Chitwan, Nepal', true, 'user', NOW() - INTERVAL '20 days'),

('Puja Maharjan', 'puja.maharjan@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Video editor and content creator. Can teach video editing and want to learn Spanish.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '18 days'),

('Suresh Limbu', 'suresh.limbu@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Fitness trainer and nutritionist. Looking to learn web development to build my own site.', 'Dharan, Nepal', true, 'user', NOW() - INTERVAL '16 days'),

('Maya Lama', 'maya.lama@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Piano teacher with 10 years experience. Interested in learning data science.', 'Pokhara, Nepal', true, 'user', NOW() - INTERVAL '14 days'),

('Binod Chaudhary', 'binod.chaudhary@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Accountant and finance professional. Want to learn photography and cooking.', 'Birgunj, Nepal', true, 'user', NOW() - INTERVAL '12 days'),

('Nisha Pandey', 'nisha.pandey@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'French language teacher. Can also teach English and want to learn yoga.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '10 days'),

('Prakash Oli', 'prakash.oli@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Cybersecurity engineer. Looking to learn guitar and improve public speaking.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '8 days'),

('Rekha Ghimire', 'rekha.ghimire@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Public speaking coach and motivational trainer. Want to learn mobile development.', 'Lalitpur, Nepal', true, 'user', NOW() - INTERVAL '6 days'),

('Aakash Basnet', 'aakash.basnet@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Cloud engineer working with AWS and Azure. Want to learn piano and cooking.', 'Kathmandu, Nepal', true, 'user', NOW() - INTERVAL '4 days'),

('Sarita KC', 'sarita.kc@gmail.com', 'pbkdf2:sha256:260000$demo$8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'Biology teacher and nature enthusiast. Looking to learn photography and web development.', 'Pokhara, Nepal', true, 'user', NOW() - INTERVAL '2 days');





UPDATE users SET password = 'HASH_HERE' WHERE email LIKE '%@gmail.com%' AND password LIKE 'pbkdf2:sha256:260000$demo$%';





INSERT INTO skills (skill_name, description, category) VALUES

-- Tech & Development
('Python', 'Programming in Python', 'Tech & Development'),
('Web Development', 'HTML, CSS, JavaScript basics', 'Tech & Development'),
('Mobile Development', 'Flutter and React Native apps', 'Tech & Development'),
('Cybersecurity', 'Network security and ethical hacking', 'Tech & Development'),
('Cloud Computing', 'AWS and Azure fundamentals', 'Tech & Development'),

-- Data & AI
('Data Science', 'Data analysis and visualization', 'Data & AI'),
('Machine Learning', 'ML algorithms and model building', 'Data & AI'),

-- Design & Visual Arts
('Graphic Design', 'Visual design using tools like Photoshop', 'Design & Visual Arts'),
('Photography', 'Portrait and landscape photography', 'Design & Visual Arts'),
('Video Editing', 'Premiere Pro and DaVinci Resolve', 'Design & Visual Arts'),
('Drawing', 'Pencil sketching and illustration', 'Design & Visual Arts'),

-- Music & Audio
('Guitar', 'Acoustic and electric guitar', 'Music & Audio'),
('Piano', 'Classical and modern piano', 'Music & Audio'),
('Music Production', 'DAW-based music production', 'Music & Audio'),
('Singing', 'Vocal training and techniques', 'Music & Audio'),

-- Writing & Languages
('English', 'English language tutoring', 'Writing & Languages'),
('French', 'French language for beginners', 'Writing & Languages'),
('Creative Writing', 'Fiction and non-fiction writing', 'Writing & Languages'),
('Public Speaking', 'Presentation and communication skills', 'Writing & Languages'),

-- Academics & Sciences
('Mathematics', 'High school and college math', 'Academics & Sciences'),
('Physics', 'Mechanics and electromagnetism', 'Academics & Sciences'),
('Biology', 'Life sciences and nature', 'Academics & Sciences'),

-- Lifestyle & Wellness
('Cooking', 'Nepali and continental cuisine', 'Lifestyle & Wellness'),
('Yoga', 'Hatha and Vinyasa yoga', 'Lifestyle & Wellness'),
('Fitness', 'Personal training and nutrition', 'Lifestyle & Wellness'),
('Meditation', 'Mindfulness and breathing techniques', 'Lifestyle & Wellness'),

-- Business & Professional
('Accounting', 'Bookkeeping and financial statements', 'Business & Professional'),
('Leadership', 'Team management and leadership skills', 'Business & Professional'),
('Finance', 'Personal and corporate finance', 'Business & Professional')

ON CONFLICT (skill_name) DO NOTHING;



-- RE-INSERT USER SKILLS WITH CORRECT CATEGORIES


-- Aarav Sharma
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'aarav.sharma@gmail.com' AND s.skill_name = 'Python';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'aarav.sharma@gmail.com' AND s.skill_name = 'Web Development';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'aarav.sharma@gmail.com' AND s.skill_name = 'Guitar';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'aarav.sharma@gmail.com' AND s.skill_name = 'Music Production';


-- Priya Thapa
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'priya.thapa@gmail.com' AND s.skill_name = 'Graphic Design';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'priya.thapa@gmail.com' AND s.skill_name = 'Drawing';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'priya.thapa@gmail.com' AND s.skill_name = 'Python';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'priya.thapa@gmail.com' AND s.skill_name = 'Photography';


-- Bikash Adhikari
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'bikash.adhikari@gmail.com' AND s.skill_name = 'Guitar';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'bikash.adhikari@gmail.com' AND s.skill_name = 'Music Production';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'bikash.adhikari@gmail.com' AND s.skill_name = 'Web Development';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'bikash.adhikari@gmail.com' AND s.skill_name = 'Python';


-- Sita Rai
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'sita.rai@gmail.com' AND s.skill_name = 'Cooking';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'sita.rai@gmail.com' AND s.skill_name = 'Photography';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'sita.rai@gmail.com' AND s.skill_name = 'Graphic Design';


-- Rohan Gurung
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'rohan.gurung@gmail.com' AND s.skill_name = 'Photography';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'rohan.gurung@gmail.com' AND s.skill_name = 'Cooking';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'rohan.gurung@gmail.com' AND s.skill_name = 'Fitness';


-- Anita Karki
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'anita.karki@gmail.com' AND s.skill_name = 'English';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'anita.karki@gmail.com' AND s.skill_name = 'Public Speaking';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'anita.karki@gmail.com' AND s.skill_name = 'Data Science';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'anita.karki@gmail.com' AND s.skill_name = 'Python';


-- Dipesh Magar
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'dipesh.magar@gmail.com' AND s.skill_name = 'Data Science';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'dipesh.magar@gmail.com' AND s.skill_name = 'Mathematics';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'dipesh.magar@gmail.com' AND s.skill_name = 'Yoga';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'dipesh.magar@gmail.com' AND s.skill_name = 'Fitness';


-- Sunita Bhandari
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'sunita.bhandari@gmail.com' AND s.skill_name = 'Yoga';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'sunita.bhandari@gmail.com' AND s.skill_name = 'Fitness';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'sunita.bhandari@gmail.com' AND s.skill_name = 'Graphic Design';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'sunita.bhandari@gmail.com' AND s.skill_name = 'Photography';


-- Nabin Shrestha
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'nabin.shrestha@gmail.com' AND s.skill_name = 'Mobile Development';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'nabin.shrestha@gmail.com' AND s.skill_name = 'Web Development';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'nabin.shrestha@gmail.com' AND s.skill_name = 'Cooking';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'nabin.shrestha@gmail.com' AND s.skill_name = 'Guitar';


-- Kamala Tamang
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'kamala.tamang@gmail.com' AND s.skill_name = 'Drawing';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'kamala.tamang@gmail.com' AND s.skill_name = 'Graphic Design';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'kamala.tamang@gmail.com' AND s.skill_name = 'Video Editing';


-- Rajan Poudel
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'rajan.poudel@gmail.com' AND s.skill_name = 'Mathematics';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'rajan.poudel@gmail.com' AND s.skill_name = 'English';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'rajan.poudel@gmail.com' AND s.skill_name = 'Python';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'rajan.poudel@gmail.com' AND s.skill_name = 'Music Production';


-- Puja Maharjan
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'puja.maharjan@gmail.com' AND s.skill_name = 'Video Editing';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'puja.maharjan@gmail.com' AND s.skill_name = 'Photography';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'puja.maharjan@gmail.com' AND s.skill_name = 'French';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'puja.maharjan@gmail.com' AND s.skill_name = 'Data Science';


-- Suresh Limbu
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'suresh.limbu@gmail.com' AND s.skill_name = 'Fitness';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'suresh.limbu@gmail.com' AND s.skill_name = 'Yoga';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'suresh.limbu@gmail.com' AND s.skill_name = 'Web Development';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'suresh.limbu@gmail.com' AND s.skill_name = 'English';


-- Maya Lama
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'maya.lama@gmail.com' AND s.skill_name = 'Piano';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'maya.lama@gmail.com' AND s.skill_name = 'Music Production';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'maya.lama@gmail.com' AND s.skill_name = 'Data Science';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'maya.lama@gmail.com' AND s.skill_name = 'Web Development';


-- Binod Chaudhary
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'binod.chaudhary@gmail.com' AND s.skill_name = 'Mathematics';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'binod.chaudhary@gmail.com' AND s.skill_name = 'Finance';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'binod.chaudhary@gmail.com' AND s.skill_name = 'Photography';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'binod.chaudhary@gmail.com' AND s.skill_name = 'Cooking';


-- Nisha Pandey
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'nisha.pandey@gmail.com' AND s.skill_name = 'French';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'nisha.pandey@gmail.com' AND s.skill_name = 'English';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'nisha.pandey@gmail.com' AND s.skill_name = 'Yoga';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'nisha.pandey@gmail.com' AND s.skill_name = 'Video Editing';


-- Prakash Oli
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'prakash.oli@gmail.com' AND s.skill_name = 'Cybersecurity';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'prakash.oli@gmail.com' AND s.skill_name = 'Cloud Computing';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'prakash.oli@gmail.com' AND s.skill_name = 'Guitar';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'prakash.oli@gmail.com' AND s.skill_name = 'Public Speaking';


-- Rekha Ghimire
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'rekha.ghimire@gmail.com' AND s.skill_name = 'Public Speaking';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'rekha.ghimire@gmail.com' AND s.skill_name = 'English';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'rekha.ghimire@gmail.com' AND s.skill_name = 'Mobile Development';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'rekha.ghimire@gmail.com' AND s.skill_name = 'Graphic Design';


-- Aakash Basnet
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'aakash.basnet@gmail.com' AND s.skill_name = 'Cloud Computing';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'aakash.basnet@gmail.com' AND s.skill_name = 'Cybersecurity';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'aakash.basnet@gmail.com' AND s.skill_name = 'Piano';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'aakash.basnet@gmail.com' AND s.skill_name = 'Cooking';


-- Sarita KC
INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'advanced'
FROM users u, skills s WHERE u.email = 'sarita.kc@gmail.com' AND s.skill_name = 'Biology';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'offer', 'intermediate'
FROM users u, skills s WHERE u.email = 'sarita.kc@gmail.com' AND s.skill_name = 'English';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'sarita.kc@gmail.com' AND s.skill_name = 'Photography';

INSERT INTO user_skills (user_id, skill_id, type, level)
SELECT u.user_id, s.skill_id, 'want', 'beginner'
FROM users u, skills s WHERE u.email = 'sarita.kc@gmail.com' AND s.skill_name = 'Web Development';