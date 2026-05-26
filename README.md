# 🔄 SkillSwap — A Local Skill Exchange Platform

> A web-based platform where people share and acquire skills without monetary transactions.

**Sirjan Lamichhane** | Enrollment No: 239150610  
BCA 6th Semester | IGNOU | BCSP-064  
Under the guidance of **Mr. Trailokya Ojha**

---

## Overview

SkillSwap is a community-driven skill exchange platform built with Python (Flask) and PostgreSQL. Instead of paying for courses or tutors, users can trade their own skills with others — teach what you know, learn what you don't.

A developer can teach Python to a guitarist, who teaches guitar in return. No money changes hands.

---

## Features

- **User Authentication** — Register, login, logout with hashed passwords
- **Profile Management** — Bio, location, and personal skill listings
- **Skill Management** — Add skills you offer and skills you want to learn
- **Matching Engine** — Automatically finds users with complementary skills and scores matches
- **Request System** — Send, accept, or reject skill exchange requests
- **Exchange Tracking** — Track active and completed exchanges
- **Notifications** — Real-time alerts for requests, acceptances, and rejections
- **Messaging** — Direct chat between matched users within an exchange
- **Ratings & Feedback** — Rate users after a completed exchange (1–5 stars)

---

## 🛠️ Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Language     | Python 3.x                        |
| Framework    | Flask (micro web framework)       |
| Database     | PostgreSQL 15+                    |
| ORM          | Flask-SQLAlchemy + psycopg2       |
| Auth         | Flask-Login + Werkzeug            |
| Frontend     | HTML5, CSS3, Jinja2 templates     |
| Dev Tools    | VS Code, pgAdmin 4, Git/GitHub    |

---

## Project Structure

```
skillswap/
├── app/
│   ├── __init__.py          # App factory, blueprints, context processor
│   ├── models.py            # All 8 SQLAlchemy database models
│   ├── auth/                # Register, login, logout
│   ├── profile/             # View/edit profile, manage skills
│   ├── matching/            # Matching engine, user discovery
│   ├── requests/            # Exchange requests, inbox, exchanges
│   ├── notifications/       # Notification system
│   ├── messages/            # Direct messaging
│   ├── ratings/             # Post-exchange ratings
│   ├── templates/           # All Jinja2 HTML templates
│   └── static/              # CSS, JS, images
├── config.py                # App configuration
├── run.py                   # Entry point
├── skillswap_db.sql     # Full PostgreSQL schema
└── requirements.txt         # Python dependencies
```

---

## Database Schema

The system uses 8 relational tables:

| Table           | Description                                      |
|-----------------|--------------------------------------------------|
| `users`         | Registered user accounts                        |
| `skills`        | Master list of all skills on the platform       |
| `user_skills`   | Junction table — links users to skills (offer/want) |
| `requests`      | Skill exchange requests between users           |
| `exchanges`     | Confirmed exchanges created on request acceptance |
| `ratings`       | Post-exchange star ratings and feedback         |
| `notifications` | Platform alerts for request/exchange events     |
| `messages`      | Direct messages within an active exchange       |

Full schema with constraints and indexes: [`skillswap_db.sql`](./skillswap_db.sql)

---

## How the Matching Engine Works

1. Fetch current user's **offered** skill IDs and **wanted** skill IDs
2. For every other active user, find:
   - Skills **they offer** that the current user **wants**
   - Skills **they want** that the current user **offers**
3. A match only exists if **both sides** have at least one skill to exchange
4. Matches are **scored** (more overlapping skills = higher score) and sorted best-first

---

## Getting Started

### Prerequisites
- Python 3.x
- PostgreSQL 15+
- pgAdmin 4 (optional but recommended)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/skillswap.git
cd skillswap
```

**2. Create and activate virtual environment**
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up the database**

Open pgAdmin and create a database named `skillswap_db`, then run the schema:
```bash
psql -U postgres -d skillswap_db -f skillswap_db.sql
```

**5. Configure the app**

Open `config.py` and update your PostgreSQL credentials:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:YOUR_PASSWORD@localhost/skillswap_db'
```

**6. Run the app**
```bash
python run.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## Requirements

```
Flask
Flask-Login
Flask-SQLAlchemy
psycopg2-binary
Werkzeug
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## Future Scope

- Native Android and iOS mobile apps
- Real-time chat using WebSockets (Flask-SocketIO)
- AI-based skill recommendations using machine learning
- Video/audio sessions via WebRTC or Zoom API
- Gamification — badges, points, and leaderboards
- Skill verification and certification system
- Multi-language support (Nepali, Hindi)
- Community forums and Q&A boards

---

## References

- [Python 3 Documentation](https://docs.python.org/3/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL 15 Documentation](https://www.postgresql.org/docs/15/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- Pressman, R. S. (2014). *Software Engineering: A Practitioner's Approach* (8th ed.)
- Date, C. J. (2003). *An Introduction to Database Systems* (8th ed.)

---

## License

This project was developed for academic purposes as part of BCSP-064 (BCA Project) at Indira Gandhi National Open University (IGNOU).
