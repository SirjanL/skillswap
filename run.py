from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # ← creates all tables in skillswap_db
        print("✅ All tables created!")
    app.run(debug=True)