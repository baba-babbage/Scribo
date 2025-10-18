from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
PASSWORD = os.getenv("NOTEBOOK_PASSWORD", "kamikaze")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Routes
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect("/notes")
    return render_template("login.html")

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if not session.get("logged_in"):
        return redirect("/")
    if request.method == "POST":
        title = request.form.get("title")
        if title:
            new_note = Note(title=title)
            db.session.add(new_note)
            db.session.commit()
        return redirect("/notes")
    all_notes = Note.query.order_by(Note.timestamp.desc()).all()
    return render_template("notes.html", notes=all_notes)

@app.route("/note/<int:id>", methods=["GET", "POST"])
def edit_note(id):
    if not session.get("logged_in"):
        return redirect("/")
    note = Note.query.get_or_404(id)
    if request.method == "POST":
        note.content = request.form.get("content")
        db.session.commit()
        return redirect("/notes")
    return render_template("edit_note.html", note=note)

@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("logged_in"):
        return redirect("/")
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect("/notes")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
